/* Build sheet loader. Supports tokens.html and motifs.html.
 *
 * Pulls the design system out of index.html at runtime instead of keeping a
 * copy. If a token or a motif changes in index.html, these sheets change with
 * it. A proof sheet that holds its own copy of the CSS will eventually lie,
 * and it will lie at the exact moment you are trusting it.
 *
 * The injected block is inserted as the FIRST child of head so the sheet's own
 * layout CSS still wins on equal specificity.
 *
 * This file is a build tool. index.html does not reference it, so the app
 * stays a single self contained file per the architecture in CLAUDE.md.
 */
(function () {
  'use strict';

  var SOURCE = 'index.html';
  var BLOCK_ID = 'wall-css';

  function reveal() {
    document.documentElement.removeAttribute('data-sheet-loading');
  }

  function fail(message) {
    var bar = document.createElement('div');
    bar.setAttribute('style', [
      'background:#FF6B4A', 'color:#2A0E06', 'padding:14px 16px',
      'font:600 14px/1.45 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif',
      'position:sticky', 'top:0', 'z-index:99'
    ].join(';'));
    bar.textContent = 'Could not load the design system from ' + SOURCE +
      '. Nothing below is trustworthy. ' + message;
    document.body.insertBefore(bar, document.body.firstChild);
    reveal();
  }

  fetch(SOURCE, { cache: 'no-store' })
    .then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status + '.');
      return res.text();
    })
    .then(function (html) {
      var block = new DOMParser()
        .parseFromString(html, 'text/html')
        .getElementById(BLOCK_ID);

      if (!block) {
        throw new Error('No style block with id "' + BLOCK_ID + '" in ' + SOURCE + '.');
      }

      var style = document.createElement('style');
      style.setAttribute('data-from', SOURCE);
      style.textContent = block.textContent;
      document.head.insertBefore(style, document.head.firstChild);

      reveal();
      document.dispatchEvent(new Event('wall-css-ready'));
    })
    .catch(function (err) {
      fail(err && err.message ? err.message : String(err));
    });
})();
