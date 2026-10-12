// Body of an `async page => { ... }` for `playwright-cli run-code`. capture.py
// prepends URL, SHOT, and WIDTH as consts. Logged out, read-only: it loads the
// published page, takes one full-page screenshot, and maps every Layout Builder
// block to its type and its place on that screenshot.
await page.setViewportSize({ width: WIDTH, height: 900 });
const resp = await page.goto(URL, { waitUntil: 'load', timeout: 45000 });
// networkidle never settles here (analytics keep polling), so give lazy
// images a moment instead.
await page.waitForTimeout(1500);
await page.evaluate(async () => {
  for (let y = 0; y < document.body.scrollHeight; y += 700) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
  scrollTo(0, 0);
});
await page.waitForTimeout(500);
const status = resp ? resp.status() : 0;
if (status === 200) await page.screenshot({ path: SHOT, fullPage: true });
const data = await page.evaluate(() => {
  const TYPES = {
    'text-field': 'Text', 'divider__wrapper': 'Divider', 'divider': 'Divider',
    'text-with-image': 'Spotlight (Landscape)', 'content-spotlight-portrait': 'Spotlight (Portrait)',
    'callouts': 'Callout', 'content-image': 'Image', 'wrapped-image': 'Wrapped Image',
    'inline-message': 'Inline Message', 'ys-view': 'View', 'quick-links': 'Quick Links',
    'accordion': 'Accordion', 'video': 'Video', 'pull-quote': 'Quote', 'media-grid': 'Media Grid',
    'facts-and-figures__group': 'Facts and Figures', 'card-collection': 'Cards',
    'custom-card-collection': 'Custom Cards', 'grand-hero-banner': 'Grand Hero',
    'cta-banner': 'Action Banner', 'image-banner': 'Image Banner', 'link-grid': 'Link Grid',
    'wrapped-callout': 'Wrapped Text Callout', 'quote-callout': 'Quote Callout', 'tiles': 'Tiles',
    'embed': 'Embed', 'video-banner': 'Video Banner', 'audio-embed': 'Audio',
    'ys-resource-view': 'Resource View',
  };
  const H = document.documentElement.scrollHeight;
  const pct = n => Math.round((n / H) * 10000) / 100;
  const W = document.documentElement.scrollWidth;
  const wpct = n => Math.round((n / W) * 10000) / 100;
  // Percentages of the full page, so the board can place them on the
  // screenshot at any display width.
  const box = el => {
    const r = el.getBoundingClientRect();
    return { top: pct(r.top + scrollY), height: pct(r.height), left: wpct(r.left + scrollX), width: wpct(r.width) };
  };

  // Rendered HTML back to the light markdown the board and drafts use.
  const md = (node) => {
    const inline = (n) => [...n.childNodes].map(c => {
      if (c.nodeType === 3) return c.textContent.replace(/\s+/g, ' ');
      if (c.nodeType !== 1) return '';
      const t = c.tagName;
      if (t === 'BR') return '\n';
      if (t === 'STRONG' || t === 'B') return `**${inline(c).trim()}**`;
      if (t === 'EM' || t === 'I') return `*${inline(c).trim()}*`;
      if (t === 'CODE') return `\`${c.textContent}\``;
      if (t === 'A') {
        const href = c.getAttribute('href') || '';
        const rel = href.replace(/^https?:\/\/yalesites\.yale\.edu/, '');
        return `[${inline(c).trim()}](${rel})`;
      }
      if (t === 'IMG') return c.alt ? `*[image: ${c.alt}]*` : '';
      return inline(c);
    }).join('');
    const out = [];
    const walk = (n) => {
      for (const c of n.children) {
        const t = c.tagName;
        if (getComputedStyle(c).display === 'none') continue;
        if (/^H[1-6]$/.test(t)) out.push(`${'#'.repeat(Math.max(2, +t[1]))} ${inline(c).trim()}`);
        else if (t === 'P') { const s = inline(c).trim(); if (s) out.push(s); }
        else if (t === 'UL' || t === 'OL') {
          out.push([...c.children].filter(li => li.tagName === 'LI')
            .map((li, i) => `${t === 'OL' ? `${i + 1}.` : '-'} ${inline(li).trim()}`).join('\n'));
        } else if (t === 'TABLE') {
          // A <br> inside a cell would end the markdown row, so cells keep it as " / ".
          const rows = [...c.querySelectorAll('tr')].map(tr => [...tr.children].map(td => inline(td).trim().replace(/\s*\n\s*/g, ' / ').replace(/\|/g, '\\|')));
          if (rows.length) {
            out.push([`| ${rows[0].join(' | ')} |`, `|${rows[0].map(() => '---').join('|')}|`,
              ...rows.slice(1).map(r => `| ${r.join(' | ')} |`)].join('\n'));
          }
        } else if (t === 'BLOCKQUOTE') out.push(`> ${inline(c).trim()}`);
        else if (t === 'IMG') { if (c.alt) out.push(`*[image: ${c.alt}]*`); }
        else if (t === 'FIGCAPTION') out.push(`*${inline(c).trim()}*`);
        else if (t === 'IFRAME') out.push(`*[embed: ${c.title || c.src}]*`);
        else if (t === 'A' && !c.querySelector('p,h2,h3,h4,li')) { const s = inline({ childNodes: [c] }).trim(); if (s) out.push(s); }
        else walk(c);
      }
    };
    walk(node);
    return out.join('\n\n').replace(/\n{3,}/g, '\n\n').trim();
  };

  const main = document.querySelector('main') || document.body;
  const sections = [...main.querySelectorAll(':scope .layout')].filter(s => !s.closest('.layout .layout'))
    .map((s, i) => ({
      index: i,
      // Multi-column sections are YDS layouts and carry their shape in a data
      // attribute (fifty-fifty, thirty-seventy) instead of a layout-- class.
      layout: s.dataset.componentLayout || ([...s.classList].find(c => c.startsWith('layout--')) || 'layout').replace('layout--', ''),
      theme: s.dataset.componentTheme || null,
      ...box(s),
    }));
  const sectionOf = el => { const s = el.closest('.layout'); return s ? [...main.querySelectorAll('.layout')].filter(x => !x.closest('.layout .layout')).indexOf(s) : -1; };
  const regionOf = el => {
    const r = el.closest('.layout__region, .yds-layout__primary, .yds-layout__secondary, .yds-layout__tertiary');
    if (!r) return '';
    const c = [...r.classList].find(c => c.startsWith('layout__region--') || c.startsWith('yds-layout__'));
    return (c || '').replace('layout__region--', '').replace('yds-layout__', '');
  };

  const blocks = [...main.querySelectorAll('.ys-block-wrapper')].filter(w => !w.parentElement.closest('.ys-block-wrapper')).map((w, i) => {
    const c = w.firstElementChild;
    let cls = c ? c.classList[0] : '';
    let type = TYPES[cls];
    if (cls === 'component-wrapper') {
      const inner = c.querySelector('.cta-group, .tabs, .webform-submission-form');
      type = !inner ? 'Component' : inner.matches('.cta-group') ? 'Button Link' : inner.matches('.tabs') ? 'Tabs' : 'Webform';
    }
    return {
      id: `b${i + 1}`,
      type: type || `Unknown (${cls})`,
      cls,
      section: sectionOf(w),
      region: regionOf(w),
      padding: (w.className.match(/--padding-(\S+)/) || [])[1] || null,
      ...box(w),
      markdown: md(w),
    };
  });

  const h1 = document.querySelector('h1');
  return {
    title: (h1 ? h1.innerText : document.title.replace(/\s*\|\s*YaleSites\s*$/, '')).trim(),
    teaser: document.querySelector('meta[name="description"]')?.content || '',
    finalUrl: location.href,
    pageHeight: H,
    sections,
    blocks,
  };
});
return { status, width: WIDTH, ...data };
