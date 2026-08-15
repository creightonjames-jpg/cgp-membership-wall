// Render every page of a PDF to a JPEG. Used to put the Core Fundamentals booklet
// into The Vault as something a phone can actually read.
//
//     swiftc -O tools/pdfpages.swift -o tools/pdfpages
//     tools/pdfpages <in.pdf> <out-dir> <prefix> [width] [quality]
//
// Why pages rather than an embedded PDF. An <iframe> or <object> pointing at a PDF
// is the obvious move and it is the wrong one here. iOS Safari routinely renders
// only the first page inside a frame, or a blank box, and this wall is opened on
// phones by 119 people. A blank box reads as broken. Page images render the same
// everywhere, lazy load, and drop straight into the Vault's existing image list, so
// there is no new viewer to write or maintain.
//
// The real PDF still ships alongside for download. This is the reading copy.
//
// CoreGraphics rather than PDFKit: fewer moving parts and it is happy headless.

import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count >= 4 else {
    FileHandle.standardError.write(
        "usage: pdfpages <in.pdf> <out-dir> <prefix> [width] [quality]\n".data(using: .utf8)!)
    exit(2)
}
let src = URL(fileURLWithPath: args[1])
let outDir = URL(fileURLWithPath: args[2])
let prefix = args[3]
let targetW = args.count > 4 ? Double(args[4]) ?? 1400 : 1400
let quality = args.count > 5 ? Double(args[5]) ?? 0.84 : 0.84

guard let doc = CGPDFDocument(src as CFURL) else {
    FileHandle.standardError.write("cannot open \(src.path)\n".data(using: .utf8)!)
    exit(1)
}
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

let space = CGColorSpaceCreateDeviceRGB()
var written: [String] = []

for i in 1...doc.numberOfPages {
    guard let page = doc.page(at: i) else { continue }
    let box = page.getBoxRect(.cropBox)
    guard box.width > 0, box.height > 0 else { continue }

    let scale = targetW / Double(box.width)
    let w = Int((Double(box.width) * scale).rounded())
    let h = Int((Double(box.height) * scale).rounded())

    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                              bytesPerRow: 0, space: space,
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { continue }

    // PDFs assume white paper. Without this, anything transparent comes out black.
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))

    ctx.interpolationQuality = .high
    ctx.scaleBy(x: CGFloat(scale), y: CGFloat(scale))
    ctx.translateBy(x: -box.origin.x, y: -box.origin.y)
    ctx.drawPDFPage(page)

    guard let img = ctx.makeImage() else { continue }
    let name = String(format: "%@-%02d.jpg", prefix, i)
    let dest = outDir.appendingPathComponent(name)
    guard let out = CGImageDestinationCreateWithURL(
        dest as CFURL, UTType.jpeg.identifier as CFString, 1, nil) else { continue }
    CGImageDestinationAddImage(out, img, [kCGImageDestinationLossyCompressionQuality: quality] as CFDictionary)
    if CGImageDestinationFinalize(out) {
        written.append(name)
        print("\(name)  \(w)x\(h)")
    }
}

print("pages written: \(written.count) of \(doc.numberOfPages)")
