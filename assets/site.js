// «Кинезио»: шапка, меню, строки «Где болит», натяжение ленты, окно врача, панель записи
;(() => {
  const $ = (s, r = document) => r.querySelector(s)
  const $$ = (s, r = document) => [...r.querySelectorAll(s)]
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches

  // Шапка получает линию снизу при прокрутке; панель записи на телефоне появляется после первого экрана
  const top = $('.top'), dock = $('.dock')
  const onScroll = () => { top.classList.toggle('scrolled', scrollY > 8); if (dock) dock.classList.toggle('on', scrollY > 420) }
  addEventListener('scroll', onScroll, { passive: true }); onScroll()

  // Мобильное меню
  const burger = $('.burger'), mnav = $('.mnav')
  burger.addEventListener('click', () => {
    const open = mnav.hidden
    mnav.hidden = !open
    burger.setAttribute('aria-expanded', String(open))
    burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню')
    document.body.style.overflow = open ? 'hidden' : ''
  })

  // Первый экран: строки заголовка поднимаются, лента натягивается
  const hero = $('.hero')
  if (hero) requestAnimationFrame(() => hero.classList.add('ready'))

  // Лента натягивается, когда попадает в экран — единственный мотив движения на сайте
  const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('on'); io.unobserve(e.target) } }), { threshold: 0.6 })
  $$('.stretch').forEach((el, i) => { if (reduce) el.classList.add('on'); else { el.style.transitionDelay = el.closest('.hero') ? `${0.35 + (i % 2) * 0.18}s` : '0s'; io.observe(el) } })

  // «Где болит»: открыта одна строка
  const zones = $$('.zone')
  zones.forEach((z) => $('.zone-btn', z).addEventListener('click', () => {
    const was = z.classList.contains('open')
    zones.forEach((x) => { x.classList.remove('open'); $('.zone-btn', x).setAttribute('aria-expanded', 'false') })
    if (!was) { z.classList.add('open'); $('.zone-btn', z).setAttribute('aria-expanded', 'true') }
  }))

  // Окно врача: данные лежат в <template id="doc-…">
  let last = null
  const close = (dlg) => { dlg.classList.remove('on'); setTimeout(() => { dlg.remove(); document.body.style.overflow = ''; last && last.focus() }, reduce ? 0 : 300) }
  $$('[data-doc]').forEach((b) => b.addEventListener('click', () => {
    const t = document.getElementById(b.dataset.doc)
    if (!t) return
    last = b
    const dlg = document.createElement('div')
    dlg.className = 'dlg'
    dlg.innerHTML = `<div class="dlg-card" role="dialog" aria-modal="true" aria-label="${b.querySelector('.dname, b')?.textContent || ''}"><button class="dlg-close" type="button" aria-label="Закрыть">×</button></div>`
    $('.dlg-card', dlg).appendChild(t.content.cloneNode(true))
    document.body.appendChild(dlg)
    document.body.style.overflow = 'hidden'
    requestAnimationFrame(() => dlg.classList.add('on'))
    $('.dlg-close', dlg).focus()
    dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.closest('.dlg-close')) close(dlg) })
    const onKey = (e) => { if (e.key === 'Escape') { close(dlg); removeEventListener('keydown', onKey) } }
    addEventListener('keydown', onKey)
  }))
})()
