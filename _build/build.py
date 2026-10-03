#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static site generator for adalworks.kz.

Run from the repo root:  python3 _build/build.py
Writes index.html, the service sub-pages, i18n/*.js and sitemap.xml.
Texts live in _build/content.py (ru, kz, en) and _build/legacy-home.json
(older home-page strings kept as they were). Jekyll skips folders that start
with "_", so this folder is not published on GitHub Pages.
"""
import html
import json
import re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import content as C  # noqa: E402

LANGS = ("ru", "kz", "en")
IDX = {"ru": 0, "kz": 1, "en": 2}
HTML_LANG = {"ru": "ru", "kz": "kk", "en": "en"}
OG_LOCALE = {"ru": "ru_KZ", "kz": "kk_KZ", "en": "en_US"}
SITE = "https://adalworks.kz"
PHONE = "+77003330999"
PHONE_TEXT = "+7 700 333 0 999"
WA = "https://wa.me/77003330999"
EMAIL = "adalworks.ads@gmail.com"
LASTMOD = "2026-10-03"

legacy = json.load(open(os.path.join(HERE, "legacy-home.json"), encoding="utf-8"))
LEGACY = {k: (legacy["ru"][k], legacy["kz"][k], legacy["en"][k]) for k in legacy["ru"]}

SERVICE_PAGES = [
    # slug, nav key, strings, image (webp, jpg, w, h), preset type for the form
    ("zhk", "navZhk", C.ZHK, ("work-wide", "jpg", 504, 389), "zhk"),
    ("biznes-centr", "navBc", C.BC, ("work-vertical-2", "jpg", 295, 520), "bc"),
    ("parking", "navParking", C.PARKING, ("work-vertical-1", "jpg", 393, 516), "parking"),
    ("aula", "navTerritory", C.TERRITORY, ("team-portrait", "jpg", 629, 666), "territory"),
]


def esc(text):
    return html.escape(text, quote=False)


def attr(text):
    return html.escape(text, quote=True)


class Page:
    def __init__(self, slug, path, default_lang, strings, ids):
        self.slug = slug
        self.path = path
        self.lang = default_lang
        self.strings = strings
        self.ids = set(ids)
        self.used = set()

    # text helpers -------------------------------------------------------
    def s(self, key):
        self.used.add(key)
        return self.strings[key][IDX[self.lang]]

    def t(self, key, tag="span", cls="", extra=""):
        c = f' class="{cls}"' if cls else ""
        return f'<{tag}{c}{extra} data-i18n="{key}">{esc(self.s(key))}</{tag}>'

    def use(self, *keys):
        for k in keys:
            self.s(k)

    def href(self, anchor):
        return f"#{anchor}" if anchor in self.ids else f"/#{anchor}"


# ---------------------------------------------------------------- partials
def picture(name, ext, w, h, alt_key, p, extra="", alt_attr=True):
    alt = attr(p.s(alt_key)) if alt_key else ""
    i18n_alt = f' data-i18n-alt="{alt_key}"' if alt_key else ""
    return (
        f'<picture><source srcset="/assets/{name}.webp" type="image/webp" />'
        f'<img src="/assets/{name}.{ext}" alt="{alt}"{i18n_alt} width="{w}" height="{h}"{extra} /></picture>'
    )


def header(p, active=None):
    sub = []
    for slug, nav_key, _s, _img, _preset in SERVICE_PAGES:
        cur = ' aria-current="page"' if slug == active else ""
        sub.append(f'<a href="/{slug}/"{cur} data-i18n="{nav_key}">{esc(p.s(nav_key))}</a>')
    sub_html = "\n            ".join(sub)
    mob_sub = "\n        ".join(s.replace("<a ", '<a class="mobile-sub" ', 1) for s in sub)
    chevron = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<polyline points="6 9 12 15 18 9"></polyline></svg>'
    )
    return f"""    <header class="site-header" data-header>
      <a class="brand" href="/" aria-label="Adal Works">
        <picture>
          <source srcset="/assets/logo.webp" type="image/webp" />
          <img src="/assets/logo.png" alt="Adal Works" width="52" height="38" />
        </picture>
        <span>Adal Works</span>
      </a>

      <nav class="desktop-nav" aria-label="{attr(p.s('navAria'))}" data-i18n-aria="navAria">
        <div class="nav-dropdown" data-dropdown>
          <button class="nav-dropdown-button" type="button" aria-expanded="false" aria-controls="services-menu" data-dropdown-button>
            {p.t('navServices')}{chevron}
          </button>
          <div class="nav-dropdown-menu" id="services-menu">
            {sub_html}
            <a href="/#services" data-i18n="navServicesAll">{esc(p.s('navServicesAll'))}</a>
          </div>
        </div>
        <a href="{p.href('how-we-work')}" data-i18n="navHow">{esc(p.s('navHow'))}</a>
        <a href="{p.href('quote')}" data-i18n="navQuote">{esc(p.s('navQuote'))}</a>
        <a href="{p.href('training-audit')}" data-i18n="navTraining">{esc(p.s('navTraining'))}</a>
        <a href="{p.href('about')}" data-i18n="navAbout">{esc(p.s('navAbout'))}</a>
        <a href="{p.href('contact')}" data-i18n="navContact">{esc(p.s('navContact'))}</a>
      </nav>

      <div class="header-actions">
        <div class="language-switch" role="group" aria-label="{attr(p.s('langAria'))}" data-i18n-aria="langAria">
          <button type="button" data-lang="ru">RU</button>
          <button type="button" data-lang="kz">KZ</button>
          <button type="button" data-lang="en">EN</button>
        </div>
        <a class="header-phone" href="tel:{PHONE}" aria-label="{PHONE_TEXT}">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"></path>
          </svg>
          <span>{PHONE_TEXT}</span>
        </a>
        <button class="menu-button" type="button" aria-label="{attr(p.s('menuOpen'))}" data-i18n-aria="menuOpen" aria-expanded="false" aria-controls="mobile-menu" data-menu-button>
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
      </div>
    </header>

    <a class="whatsapp-float" href="{WA}" data-whatsapp data-i18n-aria="whatsappFloatLabel" aria-label="{attr(p.s('whatsappFloatLabel'))}">
      <picture>
        <source srcset="/assets/whatsapp.webp" type="image/webp" />
        <img src="/assets/whatsapp.png" alt="" width="36" height="36" />
      </picture>
    </a>

    <div class="mobile-menu" id="mobile-menu" data-mobile-menu>
      <span class="mobile-menu-label" data-i18n="navServices">{esc(p.s('navServices'))}</span>
        {mob_sub}
      <a href="{p.href('how-we-work')}" data-i18n="navHow">{esc(p.s('navHow'))}</a>
      <a href="{p.href('quote')}" data-i18n="navQuote">{esc(p.s('navQuote'))}</a>
      <a href="{p.href('training-audit')}" data-i18n="navTraining">{esc(p.s('navTraining'))}</a>
      <a href="{p.href('about')}" data-i18n="navAbout">{esc(p.s('navAbout'))}</a>
      <a href="{p.href('contact')}" data-i18n="navContact">{esc(p.s('navContact'))}</a>
    </div>
"""


def hero_actions(p, wa_key):
    return f"""          <div class="hero-actions">
            <a class="button primary" href="{WA}" data-whatsapp data-i18n-whatsapp="{wa_key}" data-i18n="ctaQuote">{esc(p.s('ctaQuote'))}</a>
            <a class="button secondary" href="tel:{PHONE}" data-i18n="ctaCall">{esc(p.s('ctaCall'))}</a>
          </div>
          <p class="hero-note">{p.t('heroNote')}</p>
          <a class="text-link" href="#quote" data-i18n="ctaForm">{esc(p.s('ctaForm'))}</a>"""


def steps(p):
    p.use("stepsTag", "stepsTitle")
    items = []
    for n in range(1, 6):
        items.append(
            f"""          <li class="step-card">
            <span>{n}</span>
            {p.t(f'step{n}Title', 'h3')}
            {p.t(f'step{n}Text', 'p')}
          </li>"""
        )
    return f"""      <section class="section steps" id="how-we-work">
        <div class="section-heading">
          {p.t('stepsTag', 'p', 'eyebrow')}
          {p.t('stepsTitle', 'h2')}
        </div>
        <ol class="steps-grid">
{chr(10).join(items)}
        </ol>
      </section>
"""


def formats(p):
    def cell(key, cls=""):
        c = f' class="{cls}"' if cls else ""
        return f'<td{c} data-i18n="{key}">{esc(p.s(key))}</td>'

    rows = [
        ("fmtRowStaff", "fmtCellAw", "fmtCellAw"),
        ("fmtRowHiring", "fmtCellAw", "fmtCellAw"),
        ("fmtRowChem", "fmtCellAw", "fmtCellDiscuss"),
        ("fmtRowTools", "fmtCellAw", "fmtCellClient"),
        ("fmtRowEquip", "fmtCellAw", "fmtCellClient"),
    ]
    body = []
    for label, a, b in rows:
        ca = "is-us" if a == "fmtCellAw" else ""
        cb = "is-us" if b == "fmtCellAw" else ("is-client" if b == "fmtCellClient" else "")
        body.append(
            f'            <tr><th scope="row" data-i18n="{label}">{esc(p.s(label))}</th>{cell(a, ca)}{cell(b, cb)}</tr>'
        )
    body.append(
        f'            <tr class="fit-row"><th scope="row" data-i18n="fmtRowFit">{esc(p.s("fmtRowFit"))}</th>'
        f'{cell("fmtFitTurnkey")}{cell("fmtFitOut")}</tr>'
    )
    return f"""      <section class="section formats" id="formats">
        <div class="section-heading">
          {p.t('formatsTag', 'p', 'eyebrow')}
          {p.t('formatsTitle', 'h2')}
          {p.t('formatsLead', 'p')}
        </div>
        <div class="table-wrap">
          <table class="formats-table">
            <thead>
              <tr><th scope="col" data-i18n="fmtColItem">{esc(p.s('fmtColItem'))}</th><th scope="col" data-i18n="fmtColTurnkey">{esc(p.s('fmtColTurnkey'))}</th><th scope="col" data-i18n="fmtColOut">{esc(p.s('fmtColOut'))}</th></tr>
            </thead>
            <tbody>
{chr(10).join(body)}
            </tbody>
          </table>
        </div>
        <p class="formats-cta"><span data-i18n="fmtCta">{esc(p.s('fmtCta'))}</span> <a class="text-link" href="#quote" data-i18n="ctaForm">{esc(p.s('ctaForm'))}</a></p>
      </section>
"""


def faq(p, pairs):
    items = []
    for q, a in pairs:
        items.append(
            f"""          <details class="faq-item">
            <summary data-i18n="{q}">{esc(p.s(q))}</summary>
            <p data-i18n="{a}">{esc(p.s(a))}</p>
          </details>"""
        )
    return f"""      <section class="section faq" id="faq">
        <div class="section-heading">
          {p.t('faqTag', 'p', 'eyebrow')}
          {p.t('faqTitle', 'h2')}
        </div>
        <div class="faq-list">
{chr(10).join(items)}
        </div>
      </section>
"""


def field_label(p, key, fid=None, required=False, optional=False, tag="label"):
    for_attr = f' for="{fid}"' if fid and tag == "label" else ""
    req = '<span class="req" aria-hidden="true"> *</span>' if required else ""
    opt = (
        f' <span class="optional">({p.t("formOptional")})</span>' if optional else ""
    )
    return f'<{tag} class="field-label"{for_attr}>{p.t(key)}{req}{opt}</{tag}>'


def choice_field(p, name, label, options, required=True, kind="radio", extra_attr=""):
    req_attr = ' data-required="choice"' if required else ""
    opts = []
    for value, key in options:
        opts.append(
            f'<label class="choice"><input type="{kind}" name="{name}" value="{value}" aria-describedby="err-{name}" />{p.t(key)}</label>'
        )
    return f"""            <fieldset class="field" data-field="{name}" data-label="{label}"{req_attr}{extra_attr}>
              {field_label(p, label, required=required, optional=not required, tag='legend')}
              <div class="choice-grid">
                {(chr(10) + '                ').join(opts)}
              </div>
              <p class="field-error" id="err-{name}" data-error hidden></p>
            </fieldset>"""


def input_field(p, name, label, kind="text", required=False, hint=None, attrs="", req_kind=None, wide=False,
                placeholder=None, extra_attr="", show_optional=True):
    fid = f"q-{name}"
    req_attr = f' data-required="{req_kind or kind}"' if required else ""
    num_attr = ' data-kind="number"' if kind == "number" else ""
    describedby = f"err-{name}" + (f" hint-{name}" if hint else "")
    ph = ""
    if placeholder:
        ph = f' placeholder="{attr(p.s(placeholder))}" data-i18n-placeholder="{placeholder}"'
    if kind == "number":
        control = f'<input id="{fid}" name="{name}" type="text" inputmode="numeric" pattern="[0-9]*" autocomplete="off" aria-describedby="{describedby}"{" aria-required=\"true\"" if required else ""}{ph}{attrs} />'
    elif kind == "textarea":
        control = f'<textarea id="{fid}" name="{name}" rows="3" maxlength="600" aria-describedby="{describedby}"{ph}{attrs}></textarea>'
    else:
        control = f'<input id="{fid}" name="{name}" type="{kind}" aria-describedby="{describedby}"{" aria-required=\"true\"" if required else ""}{ph}{attrs} />'
    hint_html = f'\n              <p class="field-hint" id="hint-{name}" data-i18n="{hint}">{esc(p.s(hint))}</p>' if hint else ""
    cls = "field field-wide" if wide else "field"
    return f"""            <div class="{cls}" data-field="{name}" data-label="{label}"{req_attr}{num_attr}{extra_attr}>
              {field_label(p, label, fid, required=required, optional=show_optional and not required)}
              {control}{hint_html}
              <p class="field-error" id="err-{name}" data-error hidden></p>
            </div>"""


def select_field(p, name, label, options, required=False, extra_attr=""):
    fid = f"q-{name}"
    req_attr = ' data-required="select"' if required else ""
    opts = [f'<option value="" data-i18n="formChoose">{esc(p.s("formChoose"))}</option>']
    for value, key in options:
        opts.append(f'<option value="{value}" data-i18n="{key}">{esc(p.s(key))}</option>')
    return f"""            <div class="field" data-field="{name}" data-label="{label}"{req_attr}{extra_attr}>
              {field_label(p, label, fid, required=required, optional=not required)}
              <select id="{fid}" name="{name}" aria-describedby="err-{name}"{' aria-required="true"' if required else ''}>
                {(chr(10) + '                ').join(opts)}
              </select>
              <p class="field-error" id="err-{name}" data-error hidden></p>
            </div>"""


PERIODS = [("daily", "formPeriodDaily"), ("several", "formPeriodSeveral"), ("weekly", "formPeriodWeekly"), ("other", "formPeriodOther")]


def quote_form(p, preset=""):
    p.use("formTag", "formTitle", "formLead", "msgIntro", "msgPage", "formErrRequired", "formErrChoose", "formStdShort", "formStdLabel",
          "formErrPhone", "formErrNumber", "formErrSummary")

    def step_title(n):
        return (
            f'<h3 class="quote-step-title" id="quote-step-{n}-title" tabindex="-1">'
            f'<span class="quote-step-count">{p.t("formStepWord")} {n} {p.t("formStepOf")}</span>'
            f'{p.t(f"formStep{n}Title")}</h3>'
        )

    progress = "\n          ".join(
        f'<li data-progress="{n}"{" class=\"is-current\" aria-current=\"step\"" if n == 1 else ""}><span class="quote-progress-num" aria-hidden="true">{n}</span>{p.t(f"formStep{n}Name")}</li>'
        for n in (1, 2, 3)
    )
    step1 = "\n".join([
        choice_field(p, "type", "formType", [("zhk", "formTypeZhk"), ("bc", "formTypeBc"), ("parking", "formTypeParking"),
                                              ("territory", "formTypeTerritory"), ("other", "formTypeOther")]),
        choice_field(p, "frequency", "formFreq", [("regular", "formFreqRegular"), ("once", "formFreqOnce")]),
        choice_field(p, "format", "formFormat", [("turnkey", "formFormatTurnkey"), ("outstaff", "formFormatOut"),
                                                  ("unsure", "formFormatUnsure")], required=False)
        .replace("</fieldset>", f'  <p class="field-hint" data-i18n="formFormatHint">{esc(p.s("formFormatHint"))}</p>\n            </fieldset>'),
    ])
    zhk = "\n".join([
        input_field(p, "entrances", "formEntrances", "number", required=True),
        input_field(p, "floors", "formFloors", "text", hint="formFloorsHint", show_optional=False),
        input_field(p, "spaces_zhk", "formSpaces", "number", hint="formSpacesHint", show_optional=False),
        # standard residential format replaces the periodicity choice; sent as a short line in the message
        f"""            <div class="field field-wide form-std" data-field="std_zhk" data-label="formStdLabel" data-static="formStdShort" data-hide-once>
              {p.t('priceZhkStd', 'p', 'form-std-text')}
            </div>""",
    ])
    com = "\n".join([
        input_field(p, "area", "formArea", "number", required=True),
        input_field(p, "storeys", "formStoreys", "number"),
        input_field(p, "restrooms", "formRestrooms", "number"),
        select_field(p, "cover", "formCover", [("tile", "formCoverTile"), ("lino", "formCoverLino"), ("carpet", "formCoverCarpet"),
                                                ("concrete", "formCoverConcrete"), ("mixed", "formCoverMixed"), ("unknown", "formCoverUnknown")]),
        select_field(p, "period_com", "formPeriod", PERIODS, required=True, extra_attr=" data-hide-once"),
    ])
    parking = "\n".join([
        input_field(p, "spaces_parking", "formSpaces", "number", required=True),
        input_field(p, "parking_area", "formParkingArea", "number"),
        select_field(p, "period_parking", "formPeriod", PERIODS, required=True, extra_attr=" data-hide-once"),
    ])
    territory = "\n".join([
        choice_field(p, "season", "formSeason", [("winter", "formSeasonWinter"), ("summer", "formSeasonSummer"),
                                                  ("year", "formSeasonYear")], kind="checkbox"),
        input_field(p, "territory_area", "formTerritoryArea", "number"),
    ])
    common2 = "\n".join([
        input_field(p, "address", "formAddress", "text", placeholder="formAddressHint", wide=True, attrs=' autocomplete="street-address"',
                    show_optional=False),
        select_field(p, "start", "formStart", [("asap", "formStartAsap"), ("month", "formStartMonth"), ("plan", "formStartPlan")]),
        select_field(p, "role", "formRole", [("osi", "formRoleOsi"), ("uk", "formRoleUk"), ("owner", "formRoleOwner"), ("tenant", "formRoleTenant"), ("other", "formRoleOther")]),
    ])
    step3 = "\n".join([
        input_field(p, "name", "formName", "text", required=True, attrs=' autocomplete="name" maxlength="80"'),
        input_field(p, "phone", "formPhone", "tel", required=True, hint="formPhoneHint", req_kind="phone",
                    attrs=' autocomplete="tel" inputmode="tel" maxlength="24"'),
        input_field(p, "company", "formCompany", "text", attrs=' autocomplete="organization" maxlength="120"'),
        input_field(p, "comment", "formComment", "textarea", wide=True),
    ])
    nav_next = f'<button class="button primary" type="button" data-next>{p.t("formNext")}</button>'
    nav_back = f'<button class="button secondary" type="button" data-back>{p.t("formBack")}</button>'
    return f"""      <section class="section quote" id="quote">
        <div class="quote-intro">
          {p.t('formTag', 'p', 'eyebrow')}
          {p.t('formTitle', 'h2', extra=' id="quote-title"')}
          {p.t('formLead', 'p')}
          <ul class="quote-points">
            {p.t('formPoint1', 'li')}
            {p.t('formPoint2', 'li')}
            {p.t('formPoint3', 'li')}
          </ul>
        </div>
        <form class="quote-form" data-quote-form novalidate aria-labelledby="quote-title" data-preset-type="{preset}">
          <ol class="quote-progress">
          {progress}
          </ol>
          <div class="quote-error-summary" data-error-summary role="alert" hidden>{p.t('formErrSummary')}</div>

          <div class="quote-step" data-step="1" role="group" aria-labelledby="quote-step-1-title">
            {step_title(1)}
{step1}
            <div class="quote-actions">{nav_next}</div>
          </div>

          <div class="quote-step" data-step="2" role="group" aria-labelledby="quote-step-2-title" hidden>
            {step_title(2)}
            <div class="field-group" data-show-for="zhk">
{zhk}
            </div>
            <div class="field-group" data-show-for="bc other">
{com}
            </div>
            <div class="field-group" data-show-for="parking">
{parking}
            </div>
            <div class="field-group" data-show-for="territory">
{territory}
            </div>
            <div class="field-group">
{common2}
            </div>
            <div class="quote-actions">{nav_back}{nav_next}</div>
          </div>

          <div class="quote-step" data-step="3" role="group" aria-labelledby="quote-step-3-title" hidden>
            {step_title(3)}
            <div class="field-group">
{step3}
            </div>
            <p class="field-hint quote-privacy" data-i18n="formNote">{esc(p.s('formNote'))}</p>
            <div class="quote-actions">{nav_back}<button class="button primary" type="submit">{p.t('formSubmit')}</button></div>
          </div>
          <p class="quote-required-note" data-i18n="formRequiredNote">{esc(p.s('formRequiredNote'))}</p>

          <div class="quote-done" data-quote-done tabindex="-1" hidden>
            {p.t('formDoneTitle', 'h3')}
            {p.t('formDoneText', 'p')}
            <div class="quote-actions">
              <a class="button primary" href="{WA}" target="_blank" rel="noopener" data-done-link data-i18n="formDoneButton">{esc(p.s('formDoneButton'))}</a>
              <button class="button secondary" type="button" data-restart data-i18n="formRestart">{esc(p.s('formRestart'))}</button>
            </div>
          </div>
        </form>
      </section>
"""


def contact(p):
    return f"""      <section class="contact" id="contact">
        <div>
          {p.t('contactTag', 'p', 'eyebrow')}
          {p.t('contactTitle', 'h2')}
          {p.t('contactLead', 'p')}
        </div>
        <div class="contact-grid">
          <a href="{WA}" data-whatsapp>
            {p.t('phoneLabel')}
            <strong>{PHONE_TEXT}</strong>
          </a>
          <a href="mailto:{EMAIL}">
            <span>Email</span>
            <strong>{EMAIL}</strong>
          </a>
          <div>
            {p.t('cityLabel')}
            {p.t('cityValue', 'strong')}
          </div>
          <div>
            {p.t('hoursLabel')}
            <strong>08:00–22:00</strong>
          </div>
        </div>
      </section>
"""


def footer(p):
    services = "\n          ".join(
        f'<a href="/{slug}/" data-i18n="{nav_key}">{esc(p.s(nav_key))}</a>' for slug, nav_key, *_ in SERVICE_PAGES
    )
    return f"""    <footer class="footer">
      <div class="footer-brand">
        <a class="brand" href="/" aria-label="Adal Works">
          <picture>
            <source srcset="/assets/logo.webp" type="image/webp" />
            <img src="/assets/logo.png" alt="Adal Works" width="52" height="38" loading="lazy" />
          </picture>
          <span>Adal Works</span>
        </a>
        {p.t('footerText')}
      </div>
      <nav class="footer-col" aria-label="{attr(p.s('footerServices'))}" data-i18n-aria="footerServices">
        {p.t('footerServices', 'strong')}
          {services}
      </nav>
      <nav class="footer-col" aria-label="{attr(p.s('footerCompany'))}" data-i18n-aria="footerCompany">
        {p.t('footerCompany', 'strong')}
        <a href="{p.href('how-we-work')}" data-i18n="navHow">{esc(p.s('navHow'))}</a>
        <a href="{p.href('quote')}" data-i18n="navQuote">{esc(p.s('navQuote'))}</a>
        <a href="{p.href('training-audit')}" data-i18n="navTraining">{esc(p.s('navTraining'))}</a>
        <a href="{p.href('about')}" data-i18n="navAbout">{esc(p.s('navAbout'))}</a>
      </nav>
      <div class="footer-col">
        {p.t('footerContacts', 'strong')}
        <a href="tel:{PHONE}">{PHONE_TEXT}</a>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <span>{p.t('cityValue')} · 08:00–22:00</span>
      </div>
    </footer>
"""


def head(p, title_key, desc_key, canonical, schema_blocks, preload):
    title = attr(p.s(title_key))
    desc = attr(p.s(desc_key))
    p.use("whatsappText", "pageTitle", "pageDescription", "schemaDescription")
    alternates = "\n".join(
        f'    <meta property="og:locale:alternate" content="{OG_LOCALE[l]}" />' for l in LANGS if l != p.lang
    )
    verification = ""
    if p.slug == "home":
        verification = (
            '    <meta name="google-site-verification" content="FAzDuWo7z2bBkNbQNbmViVF--vvNtOLLbDFoWxKrhlI" />\n'
            '    <meta name="yandex-verification" content="151addc1d4f4fe84" />\n'
        )
    schemas = "\n".join(
        f'    <script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False, indent=2)}\n    </script>'
        for b in schema_blocks
    )
    return f"""<!doctype html>
<html lang="{HTML_LANG[p.lang]}" data-default-lang="{p.lang}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#f4f8ff" />
{verification}    <meta name="description" content="{desc}" />
    <title>{esc(p.s(title_key))}</title>
    <link rel="canonical" href="{canonical}" />
    <meta property="og:type" content="website" />
    <meta property="og:locale" content="{OG_LOCALE[p.lang]}" />
{alternates}
    <meta property="og:url" content="{canonical}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{desc}" />
    <meta property="og:image" content="{SITE}/assets/og-image.jpg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:site_name" content="Adal Works" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{desc}" />
    <meta name="twitter:image" content="{SITE}/assets/og-image.jpg" />
    <link rel="icon" href="/favicon.ico" sizes="any" />
    <link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/site.webmanifest" />
    <link rel="preload" href="/assets/{preload}.webp" as="image" type="image/webp" fetchpriority="high" />
    <link rel="stylesheet" href="/styles.css" />
{schemas}
  </head>
  <body>
"""


def tail(p):
    return f"""
    <script src="/i18n/{p.slug}.js" defer></script>
    <script src="/script.js" defer></script>
  </body>
</html>
"""


BUSINESS = {
    "@type": "LocalBusiness",
    "additionalType": "https://schema.org/CleaningService",
    "name": "Adal Works",
    "url": f"{SITE}/",
    "telephone": PHONE,
    "email": EMAIL,
    "address": {"@type": "PostalAddress", "addressLocality": "Astana", "addressCountry": "KZ"},
}


def home_schema(p):
    data = json.loads(json.dumps(BUSINESS))
    data = {"@context": "https://schema.org", **data}
    data.update({
        "description": p.s("schemaDescription"),
        "image": f"{SITE}/assets/og-image.jpg",
        "logo": f"{SITE}/assets/logo.png",
        "areaServed": {"@type": "City", "name": "Astana"},
        "foundingDate": "2018",
        "openingHours": "Mo-Su 08:00-22:00",
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "08:00", "closes": "22:00",
        },
        "contactPoint": {"@type": "ContactPoint", "telephone": PHONE, "contactType": "customer service",
                         "availableLanguage": ["kk", "ru", "en"]},
        "paymentAccepted": "Bank transfer",
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": C.ZHK["pageH1"][0], "url": f"{SITE}/zhk/"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": C.BC["pageH1"][0], "url": f"{SITE}/biznes-centr/"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": C.PARKING["pageH1"][0], "url": f"{SITE}/parking/"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": C.TERRITORY["pageH1"][0], "url": f"{SITE}/aula/"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": LEGACY["service6Title"][0]}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": LEGACY["training1Title"][0]}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": LEGACY["training2Title"][0]}},
            ],
        },
    })
    return [data]


# ---------------------------------------------------------------- home
def build_home():
    strings = {**LEGACY, **C.COMMON, **C.FORM, **C.HOME}
    ids = ["services", "full-cycle", "how-we-work", "formats", "territory", "parking", "pricing", "training-audit",
           "works", "facilities", "about", "faq", "quote", "contact"]
    p = Page("home", "/", "kz", strings, ids)
    out = [head(p, "pageTitle", "pageDescription", f"{SITE}/", home_schema(p), "hero-machine")]
    out.append(header(p))
    hero = f"""
    <main id="top">
      <section class="hero">
        <div class="hero-copy">
          {p.t('heroTag', 'p', 'eyebrow')}
          <h1>
            {p.t('heroTitle')}
            {p.t('heroTitleAccent', cls='hero-title-accent')}
          </h1>
          {p.t('heroLead', 'p', 'lead')}
          <div class="hero-cycle">
            {p.t('cycleTitle', 'strong')}
            <ul>
              {p.t('cycleItem1', 'li')}
              {p.t('cycleItem2', 'li')}
              {p.t('cycleItem3', 'li')}
              {p.t('cycleItem4', 'li')}
            </ul>
          </div>
{hero_actions(p, 'quoteWhatsapp')}
        </div>
        <div class="hero-media">
          <picture>
            <source srcset="/assets/hero-machine.webp" type="image/webp" />
            <img src="/assets/hero-machine.jpg" alt="Adal Works қызметкері еден жуу машинасымен" width="1707" height="1280" fetchpriority="high" />
          </picture>
          <div class="hero-panel">
            {p.t('heroPanelTop')}
            <strong>21</strong>
            {p.t('heroPanelBottom')}
          </div>
        </div>
      </section>

      <section class="stats" aria-label="Adal Works">
        <div><strong data-i18n="statYearsFigure"{' hidden' if not p.s('statYearsFigure') else ''}>{esc(p.s('statYearsFigure'))}</strong>{p.t('statYears')}</div>
        <div><strong>80</strong>{p.t('statStaff')}</div>
        <div><strong data-i18n="statFacilitiesFigure"{' hidden' if not p.s('statFacilitiesFigure') else ''}>{esc(p.s('statFacilitiesFigure'))}</strong>{p.t('statFacilities')}</div>
      </section>
"""
    out.append(hero)
    full_items = "\n".join(
        f"""          <div class="full-item">
            <span class="full-icon" aria-hidden="true">{n:02d}</span>
            {p.t(f'full{n}Title', 'h3')}
            {p.t(f'full{n}Text', 'p')}
          </div>""" for n in range(1, 5)
    )
    out.append(f"""
      <section class="section full-cycle" id="full-cycle">
        <div class="section-heading">
          {p.t('fullTag', 'p', 'eyebrow')}
          {p.t('fullTitle', 'h2')}
          {p.t('fullLead', 'p')}
        </div>
        <div class="full-grid">
{full_items}
        </div>
      </section>
""")
    segs = []
    seg_defs = [("zhk", "segZhkTitle", "segZhkText", "01"), ("biznes-centr", "segBcTitle", "segBcText", "02"),
                ("parking", "segParkingTitle", "segParkingText", "03"), ("aula", "segTerritoryTitle", "segTerritoryText", "04")]
    for slug, tk, xk, num in seg_defs:
        segs.append(f"""          <a class="service-card segment-card" href="/{slug}/">
            <span>{num}</span>
            {p.t(tk, 'h3')}
            {p.t(xk, 'p')}
            <em class="segment-more">{p.t('moreLink')} <span aria-hidden="true">→</span></em>
          </a>""")
    out.append(f"""
      <section class="section intro" id="services">
        <div class="section-heading">
          {p.t('segTag', 'p', 'eyebrow')}
          {p.t('segTitle', 'h2')}
        </div>
        <div class="segment-grid">
{chr(10).join(segs)}
        </div>
        <div class="segment-extra">
          <div>
            {p.t('segIndustrialTitle', 'h3')}
            {p.t('segIndustrialText', 'p')}
          </div>
          <a class="button secondary" href="#quote" data-i18n="ctaForm">{esc(p.s('ctaForm'))}</a>
        </div>
      </section>
""")
    out.append(steps(p))
    out.append(formats(p))
    out.append(f"""
      <section class="section territory" id="territory">
        <div class="section-heading">
          {p.t('terrTag', 'p', 'eyebrow')}
          {p.t('terrTitle', 'h2')}
          {p.t('terrLead', 'p')}
        </div>
        <div class="season-grid">
          <article class="season-card is-winter">
            {p.t('terrWinterTitle', 'h3')}
            {p.t('terrWinterText', 'p')}
          </article>
          <article class="season-card is-summer">
            {p.t('terrSummerTitle', 'h3')}
            {p.t('terrSummerText', 'p')}
          </article>
        </div>
        <a class="text-link" href="/aula/" data-i18n="terrMore">{esc(p.s('terrMore'))}</a>
      </section>

      <section class="section parking-block" id="parking">
        <div class="parking-media">
          {picture('work-vertical-1', 'jpg', 393, 516, 'parkImgAlt', p, ' loading="lazy" decoding="async"')}
        </div>
        <div class="parking-copy">
          {p.t('parkTag', 'p', 'eyebrow')}
          {p.t('parkTitle', 'h2')}
          {p.t('parkText', 'p')}
          <a class="button secondary" href="/parking/" data-i18n="parkMore">{esc(p.s('parkMore'))}</a>
        </div>
      </section>
""")
    # pricing
    zl = "\n".join(f"              {p.t(f'priceZhk{n}', 'li')}" for n in range(1, 4))
    cl = "\n".join(f"              {p.t(f'priceCom{n}', 'li')}" for n in range(1, 5))
    out.append(f"""
      <section class="section pricing" id="pricing">
        <div class="pricing-copy">
          {p.t('priceTag', 'p', 'eyebrow')}
          {p.t('priceTitle', 'h2')}
          {p.t('priceLead', 'p')}
          <div class="pricing-actions">
            <a class="button primary" href="#quote" data-i18n="ctaForm">{esc(p.s('ctaForm'))}</a>
            <a class="button secondary" href="{WA}" data-whatsapp data-i18n-whatsapp="priceWhatsapp" data-i18n="priceButton">{esc(p.s('priceButton'))}</a>
          </div>
        </div>
        <div class="price-factors">
          <div>
            {p.t('priceZhkTitle', 'strong')}
            <ul>
{zl}
            </ul>
            {p.t('priceZhkStd', 'p', 'price-std')}
          </div>
          <div>
            {p.t('priceComTitle', 'strong')}
            <ul>
{cl}
            </ul>
          </div>
        </div>
      </section>
""")
    # legacy sections: training/audit, works, facilities, about, certificates (copied markup, absolute asset paths)
    out.append(legacy_sections(p))
    out.append(faq(p, [("faqPriceQ", "faqPriceA"), ("qFreeQ", "qFreeA"), ("qPayQ", "qPayA"), ("qFormatsQ", "qFormatsA"),
                       ("faqOsiQ", "faqOsiA"), ("faqOneQ", "faqOneA"), ("qSnowQ", "qSnowA"), ("qParkingQ", "qParkingA"),
                       ("faqTrainingQ", "faqTrainingA")]))
    out.append(quote_form(p))
    out.append(contact(p))
    out.append("    </main>\n\n")
    out.append(footer(p))
    out.append(tail(p))
    return p, "".join(out)


def marquee(items, cls, track_cls, label, size):
    w, h = size
    pics = []
    for name, ext, alt in items:
        pics.append(f'<picture><source srcset="/assets/{name}.webp" type="image/webp" /><img src="/assets/{name}.{ext}" alt="{attr(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async" /></picture>')
    for name, ext, _alt in items:
        pics.append(f'<picture><source srcset="/assets/{name}.webp" type="image/webp" /><img src="/assets/{name}.{ext}" alt="" aria-hidden="true" width="{w}" height="{h}" loading="lazy" decoding="async" /></picture>')
    inner = "\n            ".join(pics)
    return f"""        <div class="photo-marquee {cls}" aria-label="{attr(label)}">
          <div class="marquee-track {track_cls}">
            {inner}
          </div>
        </div>"""


def legacy_sections(p):
    def li(key):
        return p.t(key, "li")
    work = marquee([("work-wide", "jpg", "Коммерциялық нысанды тазалау"), ("work-vertical-1", "jpg", "Клининг жұмыс процесі"),
                    ("work-square", "jpg", "Аумақты кәсіби тазалау"), ("work-vertical-2", "jpg", "Тазалау кезіндегі Adal Works қызметкері"),
                    ("team-office", "jpg", "Нысандағы команда")], "work-gallery", "", "Adal Works жұмыстарының фотолары", (460, 340))
    fac = marquee([("object-1", "png", "Adal Works қызмет көрсететін нысан"), ("object-2", "png", "Қызмет көрсетілетін тұрғын үй кешені"),
                   ("object-3", "png", "Коммерциялық нысан"), ("object-4", "png", "Нысан аумағы"),
                   ("team-portrait", "jpg", "Adal Works командасы")], "facility-strip", "reverse-speed", "Нысандар фотолары", (300, 210))
    about = marquee([("work-wide", "jpg", "Нысанды кәсіби тазалау"), ("work-vertical-1", "jpg", "Adal Works командасының жұмысы"),
                     ("work-square", "jpg", "Аумақты тазалау"), ("work-vertical-2", "jpg", "Adal Works қызметкері"),
                     ("hero-team", "jpg", "Сертификаттары бар Adal Works командасы")], "about-media", "about-track", "Adal Works жұмыстарының фотолары", (310, 360))
    certs = marquee([(f"cert-{n}", "png", "Adal Works сертификаты") for n in range(1, 8)], "certificate-grid", "certificate-track",
                    "Adal Works сертификаттары", (210, 260))
    tr_wa1 = WA
    p.use("training1Whatsapp", "training2Whatsapp")
    return f"""
      <section class="section training-audit" id="training-audit">
        <div class="section-heading">
          {p.t('navTraining', 'p', 'eyebrow')}
          {p.t('trainingTitle', 'h2')}
          {p.t('trainingLead', 'p')}
        </div>
        <div class="training-method">
          {p.t('trainingMethodTitle', 'h3')}
          {p.t('trainingMethod', 'p')}
        </div>
        <div class="training-grid">
          <article class="training-card">
            {p.t('training1Title', 'h3')}
            {p.t('training1Intro', 'p')}
            <ul>
              {li('training1Point1')}
              {li('training1Point2')}
              {li('training1Point3')}
              {li('training1Point4')}
            </ul>
            <a class="button primary" href="{tr_wa1}" data-whatsapp data-i18n-whatsapp="training1Whatsapp" data-i18n="training1Button">{esc(p.s('training1Button'))}</a>
          </article>
          <article class="training-card">
            {p.t('training2Title', 'h3')}
            {p.t('training2Intro', 'p')}
            <ul>
              {li('training2Point1')}
              {li('training2Point2')}
              {li('training2Point3')}
              {li('training2Point4')}
            </ul>
            <a class="button primary" href="{tr_wa1}" data-whatsapp data-i18n-whatsapp="training2Whatsapp" data-i18n="training2Button">{esc(p.s('training2Button'))}</a>
          </article>
        </div>
      </section>
""" + f"""
      <section class="section work-section" id="works">
        <div class="section-heading compact">
          {p.t('worksTag', 'p', 'eyebrow')}
          {p.t('worksTitle', 'h2')}
        </div>
{work}
      </section>

      <section class="section facilities" id="facilities">
        <div class="section-heading compact">
          {p.t('facilitiesTag', 'p', 'eyebrow')}
          {p.t('facilitiesTitle', 'h2')}
        </div>
{fac}
      </section>

      <section class="section about" id="about">
{about}
        <div class="about-copy">
          {p.t('aboutTag', 'p', 'eyebrow')}
          {p.t('aboutTitle', 'h2')}
          {p.t('aboutText', 'p')}
          <div class="proof-list">
            <div>
              {p.t('proof1Title', 'strong')}
              {p.t('proof1Text')}
            </div>
            <div>
              {p.t('proof2Title', 'strong')}
              {p.t('proof2Text')}
            </div>
            <div>
              {p.t('proof3Title', 'strong')}
              {p.t('proof3Text')}
            </div>
          </div>
        </div>
      </section>

      <section class="section certificates">
        <div class="section-heading compact">
          {p.t('certTag', 'p', 'eyebrow')}
          {p.t('certTitle', 'h2')}
        </div>
{certs}
      </section>
"""


# ---------------------------------------------------------------- service pages
def build_service(slug, nav_key, page_strings, image, preset):
    strings = {**C.COMMON, **C.FORM, **{k: v for k, v in C.HOME.items() if k.startswith(("price", "terr", "seg"))}, **page_strings}
    has_formats = slug in ("zhk", "biznes-centr")
    ids = ["includes", "pricing", "how-we-work", "faq", "quote", "related", "contact"] + (["formats"] if has_formats else [])
    p = Page(slug, f"/{slug}/", "ru", strings, ids)
    canonical = f"{SITE}/{slug}/"
    service_schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": page_strings["pageH1"][0],
        "description": page_strings["schemaDescription"][0],
        "serviceType": C.COMMON[nav_key][0],
        "url": canonical,
        "areaServed": {"@type": "City", "name": "Astana"},
        "provider": BUSINESS,
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Adal Works", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": C.COMMON[nav_key][0], "item": canonical},
        ],
    }
    name, ext, w, h = image
    out = [head(p, "pageTitle", "pageDescription", canonical, [service_schema, crumbs], name)]
    out.append(header(p, active=slug))
    out.append(f"""
    <main id="top" class="service-page">
      <section class="hero page-hero">
        <div class="hero-copy">
          <nav class="breadcrumbs" aria-label="{attr(p.s('crumbAria'))}" data-i18n-aria="crumbAria">
            <ol>
              <li><a href="/" data-i18n="crumbHome">{esc(p.s('crumbHome'))}</a></li>
              <li><a href="/#services" data-i18n="navServices">{esc(p.s('navServices'))}</a></li>
              <li aria-current="page" data-i18n="{nav_key}">{esc(p.s(nav_key))}</li>
            </ol>
          </nav>
          {p.t('pageHeroTag', 'p', 'eyebrow')}
          {p.t('pageH1', 'h1')}
          {p.t('pageLead', 'p', 'lead')}
{hero_actions(p, 'pageWhatsapp')}
        </div>
        <div class="hero-media">
          {picture(name, ext, w, h, 'pageImgAlt', p, ' fetchpriority="high"')}
        </div>
      </section>
""")
    inc_nums = sorted(int(k[3:-5]) for k in page_strings if k.startswith("inc") and k.endswith("Title") and k[3:-5].isdigit())
    n_inc = len(inc_nums)
    inc = "\n".join(
        f"""          <article class="service-card">
            <span>{i:02d}</span>
            {p.t(f'inc{n}Title', 'h3')}
            {p.t(f'inc{n}Text', 'p')}
          </article>""" for i, n in enumerate(inc_nums, 1)
    )
    out.append(f"""
      <section class="section intro" id="includes">
        <div class="section-heading">
          {p.t('incTag', 'p', 'eyebrow')}
          {p.t('incTitle', 'h2')}
        </div>
        <div class="service-grid{' is-four' if n_inc == 4 else ' is-five' if n_inc == 5 else ''}">
{inc}
        </div>
      </section>
""")
    if "planTitle" in page_strings:
        out.append(f"""
      <section class="section plan-callout">
        <div>
          {p.t('planTitle', 'h2')}
          {p.t('planText', 'p')}
        </div>
        <a class="button primary" href="#quote" data-i18n="ctaForm">{esc(p.s('ctaForm'))}</a>
      </section>
""")
    if has_formats:
        out.append(formats(p))
    if slug == "zhk":
        params = [f"priceZhk{n}" for n in range(1, 4)]
    elif slug == "biznes-centr":
        params = [f"priceCom{n}" for n in range(1, 5)]
    elif slug == "parking":
        params = ["pp1", "pp2", "pp3"]
    else:
        params = ["tp1", "tp2", "tp3"]
    plist = "\n".join(f"            {p.t(k, 'li')}" for k in params)
    std_note = f"\n            {p.t('priceZhkStd', 'p', 'price-std')}" if slug == "zhk" else ""
    out.append(f"""
      <section class="section pricing page-pricing" id="pricing">
        <div class="pricing-copy">
          {p.t('priceTag', 'p', 'eyebrow')}
          {p.t('pagePriceTitle', 'h2')}
          {p.t('pagePriceLead', 'p')}
          <div class="pricing-actions">
            <a class="button primary" href="#quote" data-i18n="ctaForm">{esc(p.s('ctaForm'))}</a>
            <a class="button secondary" href="{WA}" data-whatsapp data-i18n-whatsapp="pageWhatsapp" data-i18n="priceButton">{esc(p.s('priceButton'))}</a>
          </div>
        </div>
        <div class="price-factors single">
          <div>
            <ul>
{plist}
            </ul>{std_note}
          </div>
        </div>
      </section>
""")
    out.append(steps(p))
    pairs = [(f"pq{n}Q", f"pq{n}A") for n in range(1, 4) if f"pq{n}Q" in page_strings]
    shared = {"zhk": [("qFreeQ", "qFreeA"), ("qFormatsQ", "qFormatsA"), ("qParkingQ", "qParkingA")],
              "biznes-centr": [("qFormatsQ", "qFormatsA"), ("qFreeQ", "qFreeA"), ("qPayQ", "qPayA")],
              "parking": [("qParkingQ", "qParkingA"), ("qSnowQ", "qSnowA"), ("qFreeQ", "qFreeA"), ("qPayQ", "qPayA")],
              "aula": [("qSnowQ", "qSnowA"), ("qFreeQ", "qFreeA"), ("qPayQ", "qPayA")]}[slug]
    if slug in ("parking", "aula"):
        pairs = shared[:1] + pairs + shared[1:]
    else:
        pairs = pairs[:1] + shared + pairs[1:]
    out.append(faq(p, pairs))
    out.append(quote_form(p, preset))
    rel = []
    for s2, nk, *_ in SERVICE_PAGES:
        if s2 == slug:
            continue
        rel.append(f'<a class="related-link" href="/{s2}/"><span data-i18n="{nk}">{esc(p.s(nk))}</span><span aria-hidden="true">→</span></a>')
    rel.append(f'<a class="related-link" href="/#services"><span data-i18n="navServicesAll">{esc(p.s("navServicesAll"))}</span><span aria-hidden="true">→</span></a>')
    out.append(f"""
      <section class="section related" id="related">
        {p.t('relatedTitle', 'h2')}
        <div class="related-grid">
          {(chr(10) + '          ').join(rel)}
        </div>
      </section>
""")
    out.append(contact(p))
    out.append("    </main>\n\n")
    out.append(footer(p))
    out.append(tail(p))
    return p, "".join(out)


def write_i18n(p, html_text=""):
    # keys referenced only through attributes (e.g. data-i18n-whatsapp) also need exporting
    for key in re.findall(r'data-i18n-whatsapp="([^"]+)"', html_text):
        if key in p.strings:
            p.used.add(key)
    data = {lang: {} for lang in LANGS}
    for key in sorted(p.used):
        for lang in LANGS:
            data[lang][key] = p.strings[key][IDX[lang]]
    os.makedirs(os.path.join(ROOT, "i18n"), exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "i18n", f"{p.slug}.js"), "w", encoding="utf-8") as fh:
        fh.write("// Generated by _build/build.py — edit _build/content.py instead.\n")
        fh.write(f"window.ADAL_I18N = {body};\n")


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)


def main():
    p, html_text = build_home()
    write("index.html", html_text)
    write_i18n(p, html_text)
    urls = [("/", "1.0")]
    for slug, nav_key, strings, image, preset in SERVICE_PAGES:
        sp, text = build_service(slug, nav_key, strings, image, preset)
        write(f"{slug}/index.html", text)
        write_i18n(sp, text)
        urls.append((f"/{slug}/", "0.8"))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio in urls:
        sitemap += ["  <url>", f"    <loc>{SITE}{path}</loc>", f"    <lastmod>{LASTMOD}</lastmod>",
                    "    <changefreq>weekly</changefreq>", f"    <priority>{prio}</priority>", "  </url>"]
    sitemap.append("</urlset>")
    write("sitemap.xml", "\n".join(sitemap) + "\n")
    print("built", len(urls), "pages")


if __name__ == "__main__":
    main()
