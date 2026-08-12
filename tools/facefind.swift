// Find faces in images and print them as JSON. Used by tools/recrop-headshots.py.
//
//     swiftc -O tools/facefind.swift -o tools/facefind
//     tools/facefind a.jpg b.jpg ...
//
// Why Swift and not Python. The cv2 build on this Mac is headless and ships no
// haarcascade XML, and Haar is poor on the angled, bespectacled, outdoors phone
// photos that make up most of this set anyway. macOS Vision is already installed,
// is far better on exactly those cases, and needs no model download.
//
// Output is one JSON object per line, so a failure on one file cannot spoil the
// batch. Coordinates are PIXELS with the origin at the TOP LEFT, because that is
// what Pillow's crop wants. Vision reports normalized coordinates from the bottom
// left, so the y flip happens here, once, rather than in every caller.
//
// Callers should hand this orientation-normalized images. This tool does not apply
// EXIF rotation. Mixing a rotated source with an unrotated face box is what made
// the first re-crop attempt cut the tops off heads.

import Foundation
import Vision
import CoreImage
import ImageIO

func faces(in url: URL) throws -> (Int, Int, [[String: Double]]) {
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
          let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        throw NSError(domain: "facefind", code: 1,
                      userInfo: [NSLocalizedDescriptionKey: "could not decode"])
    }
    let w = cg.width, h = cg.height

    let req = VNDetectFaceRectanglesRequest()
    // revision 3 is the CoreML detector. Better on profiles and partial faces.
    if VNDetectFaceRectanglesRequest.supportedRevisions.contains(3) {
        req.revision = 3
    }
    try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])

    var out: [[String: Double]] = []
    for obs in (req.results ?? []) {
        let b = obs.boundingBox              // normalized, origin bottom left
        out.append([
            "x":          b.origin.x * Double(w),
            "y":          (1.0 - b.origin.y - b.size.height) * Double(h),  // flip to top left
            "w":          b.size.width * Double(w),
            "h":          b.size.height * Double(h),
            "confidence": Double(obs.confidence),
            "roll":       obs.roll?.doubleValue ?? 0,
            "yaw":        obs.yaw?.doubleValue ?? 0
        ])
    }
    // Biggest face first. On a photo with a bystander, the subject is the big one.
    out.sort { ($0["w"]! * $0["h"]!) > ($1["w"]! * $1["h"]!) }
    return (w, h, out)
}

func emit(_ o: [String: Any]) {
    if let d = try? JSONSerialization.data(withJSONObject: o),
       let s = String(data: d, encoding: .utf8) {
        print(s)
    }
}

for path in CommandLine.arguments.dropFirst() {
    let url = URL(fileURLWithPath: path)
    do {
        let (w, h, f) = try faces(in: url)
        emit(["path": path, "width": w, "height": h, "faces": f])
    } catch {
        emit(["path": path, "error": error.localizedDescription])
    }
}
