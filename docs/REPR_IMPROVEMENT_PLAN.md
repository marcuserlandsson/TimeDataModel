# Repr & visualization improvement plan

This document outlines how to level up the CLI and notebook repr experience: fix known issues and add frontend polish so the data model looks and behaves great everywhere.

---

## Current state (recap)

- **`_repr.py`** holds all display logic: CSS, `_render_box`, `_build_repr_html`, `CoverageBar`, `HierarchyTree`, and mixins for each data class.
- **Terminal**: Unicode box (`┌─┐│└┘`) with meta block and data block; width can grow with content.
- **Notebook**: HTML with themed CSS (light/dark), meta table, data table, hover states.
- **Theme**: `theme.json` + `_theme.py`; colors for header, meta, data, coverage, etc.

---

## Known issues to fix

### 1. HTML “short” data: not all rows shown

In `_build_repr_html`, when `show_all` is true (e.g. `n_rows <= 2*max_preview+1`), only `head_rows` (first `max_preview` rows) are emitted; `tail_rows` is intentionally empty. So for 5 rows we show 3, not 5.

**Fix:** When `show_all` is true, emit all row indices (e.g. `range(n_rows)`). When false, keep current head → ellipsis → tail behavior.

### 2. Terminal: dynamic width and long lines

- **No default max width:** `get_repr_width()` is `None`, so the box grows to the longest line (e.g. long “Labels” or “Description”). In a narrow terminal this overflows or wraps badly.
- **Meta lines:** `_format_meta_lines` uses fixed `label_w=18`. Long values are not truncated when no `max_width` is set, so one long value dictates box width.
- **Alignment:** Meta uses `label: value`; data rows use left for index and right for values. That’s good; the main issue is width control.

**Fix:**

- Introduce a **sensible default max width** for the terminal (e.g. 80, or from `shutil.get_terminal_size().columns` when available), so `_render_box` gets a `max_width` unless the user explicitly sets `set_repr_width(None)`.
- When building terminal content, **respect max width early**: truncate or wrap long meta values to the chosen content width before building `content_lines`, and ensure data column widths are capped so the total line length does not exceed that.

### 3. HTML: layout and alignment

- **Fixed max-width:** `.ts-repr { max-width: 640px }` is good for containment but can make wide tables feel cramped.
- **Table columns:** No explicit column width or `table-layout` strategy for the data table; timestamp vs value columns may not share space optimally.
- **Meta table:** `table-layout: fixed` with first column 90px; second column can squash long values (ellipsis). Consider `min-width` on the index column so it doesn’t shrink too much.

**Fix:**

- Keep a max-width but consider making it configurable (e.g. CSS variable or data attribute) so notebooks can override.
- Data table: set **index column(s)** to a sensible `min-width` and `text-align: left`; **value columns** to `text-align: right` and allow them to share remaining space (e.g. `width: 1%` on index so data columns take the rest, or explicit `table-layout: fixed` with proportional column behavior).
- Ensure numeric cells use consistent right alignment and monospace so decimals line up.

---

## Frontend “magic” improvements

### CLI (terminal)

1. **Default width:** Use terminal width when available (`shutil.get_terminal_size()`), fallback to 80; allow `set_repr_width(None)` for “no limit”.
2. **Truncation / wrapping:** When max width is set, truncate long meta values (with “…”) and optionally wrap very long descriptions to multiple lines within the box (if we want to support multi-line meta).
3. **Visual hierarchy:** Keep the existing separator line between meta and data; consider a subtle difference (e.g. no extra padding) so the two blocks are clearly distinct.
4. **Consistent padding:** Ensure `_format_meta_lines` and data row formatting both respect the same content width so the box is rectangular and aligned.

### HTML (notebook)

1. **Table layout**
   - Index column: `min-width`, left-aligned, stable so timestamps don’t jump.
   - Data columns: right-aligned, monospace; optional `white-space: nowrap` for numbers so alignment is preserved.
   - Optional: **sticky header** for long tables (e.g. `position: sticky; top: 0` on `thead` inside a scrollable container if we add max-height).

2. **Polish**
   - Slight **border-radius** on `.ts-repr` and maybe header for a card-like look.
   - Optional **box-shadow** for depth (themeable if we add tokens).
   - Ensure **focus/outline** for accessibility when navigating with keyboard.

3. **Responsiveness**
   - On narrow viewports, consider horizontal scroll on the data table instead of squashing columns (e.g. `overflow-x: auto` on `.ts-data`).
   - Meta section: keep label + value on one line where possible; ellipsis on long values is already there.

4. **Theme**
   - Add optional theme keys if needed: e.g. `repr_border_radius`, `repr_shadow`, `data_cell_border` for future tweaks without code changes.

### CoverageBar & HierarchyTree

- **CoverageBar:** Already has SVG and terminal bar; ensure colors and labels are readable in both themes; optional tooltip (title) on SVG segments for “from–to” or coverage %.
- **HierarchyTree:** HTML `<details>` is good; consider a bit of spacing and indentation so hierarchy is obvious; ensure dark theme colors are applied if not already.

---

## Premium visual polish (notebook & CLI)

These changes push the repr from “clean and functional” to “premium product” feel: intentional typography, depth, spacing, and micro-details that read as designed, not default.

### Typography

- **Header:** Slightly larger size (e.g. 15px), semibold (600) or bold (700), and optional `letter-spacing: 0.02em` so the class name feels like a title, not inline text.
- **Data table:** Use `font-variant-numeric: tabular-nums` (and keep monospace) so digits align vertically in numeric columns; decimals line up without extra hacks.
- **Meta labels:** Keep current weight (600); ensure a clear contrast ratio with meta values (WCAG AA).
- **Optional:** Use a system UI font stack for the header only (e.g. `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`) while keeping monospace for meta and data, so the card has a clear “title vs data” hierarchy.

### Spacing and rhythm

- **Consistent scale:** Base padding on a 4px or 6px grid (e.g. header `10px 14px`, meta/data `8px 12px`, cell padding `4px 10px`). Avoid arbitrary 6/10/8 mixes.
- **Section breathing room:** Slightly more space between meta block and data block (e.g. margin or padding) so the two sections read as distinct.
- **Line height:** Set `line-height: 1.45` or `1.5` on data rows so multi-line cells (if any) and timestamps don’t feel cramped.
- **Empty state:** Give “(empty)” its own styling: centered, muted color (e.g. theme `ellipsis` or a dedicated `empty_state_text`), padding `12px 16px`, and optionally a slightly larger or italic style so it reads as an intentional empty state, not a bare string.

### Depth and containment

- **Card container:** Add `border-radius: 8px` (or theme token `repr_border_radius`) to `.ts-repr`; optionally `border-radius: 8px 8px 0 0` on the header so the top reads as one card.
- **Border:** A 1px solid outer border using a theme color (e.g. light: `#e5e7eb`, dark: `#334155`) so the card has a clear edge; combine with radius for a “floating card” look.
- **Shadow:** Light theme: `box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04)`; dark: `0 2px 6px rgba(0,0,0,.2)` or similar. Keeps the repr from feeling flat; stay subtle so it doesn’t distract.
- **Header subtle gradient (optional):** Very light gradient on header bg, e.g. `linear-gradient(180deg, #f8f9fa 0%, #f0f0f0 100%)` in light mode, for a slight “bar” feel without being loud.

### Data table refinement

- **Row borders:** Optional very subtle row separator, e.g. `border-bottom: 1px solid rgba(0,0,0,.06)` (light) / `rgba(255,255,255,.06)` (dark) for scanability in long tables; or skip if hover alone is enough.
- **Zebra striping (optional):** For long tables, `tbody tr:nth-child(odd)` with a 2–3% opacity overlay of the table bg or a dedicated theme key; keep it very subtle so it doesn’t compete with hover.
- **Sticky header:** If the data block gets `max-height` and `overflow-y: auto`, make `thead` sticky with `position: sticky; top: 0; z-index: 1`, a background (same as current header row), and a thin `box-shadow` under it on scroll so the header stays readable.
- **Numeric alignment:** Ensure all value cells are `text-align: right`, `font-variant-numeric: tabular-nums`, and `white-space: nowrap` (or allow wrap only when needed) so numbers don’t jump.

### Micro-interactions and states

- **Hover:** Add `transition: background-color .12s ease` (or `.15s`) on `tr` so hover doesn’t feel instant; same for any interactive element in CoverageBar/HierarchyTree.
- **Focus:** For keyboard users, a clear `outline` or `box-shadow` on focus (e.g. `:focus-visible`) that matches the theme; avoid removing focus outline without a visible replacement.
- **Selection:** If users can select table text, ensure `user-select: text` on data cells and that selection color has enough contrast.

### Accent and identity (optional)

- **Header accent:** A thin (2–3px) left or bottom border on the header in an accent color (e.g. theme key `accent` or a blue/slate) to give the card a small “brand” touch without changing the rest of the palette.
- **Theme extension:** New optional keys: `repr_border_radius`, `repr_shadow`, `repr_border`, `empty_state_text`, `accent`, `zebra_stripe` so power users can tune the premium look without forking CSS.

### CoverageBar and HierarchyTree

- **CoverageBar SVG:** Use `rx="2"` (or similar) on `<rect>` segments for rounded bar chunks; optional subtle gradient on “present” segments (e.g. `linearGradient` light→slightly darker) for depth.
- **HierarchyTree:** In HTML, use a vertical `border-left` on the tree container or each level with a muted color so the hierarchy reads as a clear tree; ensure `<summary>` has consistent font-weight and padding.

### Terminal (CLI)

- **Rounded box (optional):** Use Unicode rounded box-drawing for a softer look: `╭` `╮` `╯` `╰` and `─` `│` (U+2560 block) instead of `┌┐└┘` and `─│`; or keep sharp corners for consistency with classic terminals.
- **Optional ANSI color:** If stdout is a TTY, use faint ANSI colors for meta labels vs values (e.g. dim for labels, default for values) so the terminal repr has a bit of hierarchy; detect with `sys.stdout.isatty()` and keep it subtle (e.g. dim only).

---

## Suggested implementation order

| Priority | Task | Notes |
|----------|------|--------|
| 1 | Fix HTML `show_all` rows in `_build_repr_html` | Small change; fixes wrong row count for short series. |
| 2 | Terminal: default max width (terminal size or 80) | Prevents huge boxes; integrate with existing `set_repr_width`. |
| 3 | Terminal: truncate long meta/data lines to max width | When building content_lines, cap line length and use `_truncate` so box stays within width. |
| 4 | HTML: data table column layout and alignment | min-width index, right-align values, `tabular-nums`, optional sticky header. |
| 5 | HTML: premium container (radius, border, shadow) | Card look; optional theme keys `repr_border_radius`, `repr_shadow`, `repr_border`. |
| 6 | HTML: spacing rhythm and empty state | Consistent padding scale; styled “(empty)” with muted color and padding. |
| 7 | HTML: typography (header hierarchy, tabular-nums) | Header letter-spacing/size; tabular-nums on data; optional system font for header. |
| 8 | HTML: micro-interactions (hover transition, focus) | Short transition on hover; visible focus for a11y. |
| 9 | CoverageBar / HierarchyTree polish | Rounded SVG rects; tree border/indentation; optional tooltips. |
| 10 | Terminal: optional rounded box or ANSI hint | Low priority; rounded Unicode or faint TTY colors. |

---

## Files to touch

- **`timedatamodel/_repr.py`**: `_build_repr_html` (show_all fix), `_render_box` and callers (default width, truncation), `_format_meta_lines` (optional width param), `_TimeSeriesBaseReprMixin.__repr__` (use default width and cap line lengths), CSS in `_repr_css()` (layout and polish).
- **`timedatamodel/_theme.py`** / **`timedatamodel/theme.json`**: Optional new keys for repr styling (can be added incrementally).
- **Tests**: Any existing repr tests (e.g. snapshot or string checks) should be updated for the HTML row count and terminal width behavior; add tests for “short” series and for `set_repr_width(None)` vs default.

---

## Summary

- Fix the HTML bug so short series show all rows.
- Make terminal repr width-aware by default and truncate long lines so the box stays readable.
- Improve HTML table layout (index vs data columns, alignment, overflow) and add light visual polish.
- **Premium polish:** Typography hierarchy, spacing rhythm, card depth (radius/border/shadow), styled empty state, tabular-nums, hover/focus micro-interactions, optional accent and theme tokens. CoverageBar and HierarchyTree get small refinements; terminal can get optional rounded box or faint ANSI colors.
- Keep theme and structure as-is where possible; extend theme only where it pays off (e.g. `repr_border_radius`, `repr_shadow`, `accent`, `empty_state_text`).

After this, the CLI and notebook views should feel consistent, readable, and like a premium product rather than a hobby project.
