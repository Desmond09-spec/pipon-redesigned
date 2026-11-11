import { useEffect, useRef, useState } from 'react';

/* ---------------------------------- hero variants ----------------------------- */

const HERO_VARIANTS = ['original', 'reaim', 'brand'];
const DEFAULT_VARIANT = 'brand';

function useHeroVariant() {
  const read = () => {
    const value = new URLSearchParams(window.location.search).get('hero');
    return HERO_VARIANTS.includes(value) ? value : DEFAULT_VARIANT;
  };
  const [variant, setVariant] = useState(read);
  const [compare] = useState(
    () => new URLSearchParams(window.location.search).get('compare') === '1'
  );

  const select = (next) => {
    const url = new URL(window.location.href);
    if (next === DEFAULT_VARIANT) url.searchParams.delete('hero');
    else url.searchParams.set('hero', next);
    window.history.replaceState({}, '', url);
    setVariant(next);
  };
  return { variant, compare, select };
}

function usePortrait() {
  const [portrait, setPortrait] = useState(
    () => window.matchMedia('(max-width: 1023px)').matches
  );
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 1023px)');
    const onChange = (event) => setPortrait(event.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);
  return portrait;
}

function HeroSwitcher({ variant, select }) {
  return (
    <div className="hero-switcher" role="group" aria-label="Hero variant">
      <span className="hero-switcher__label">Hero</span>
      {HERO_VARIANTS.map((value) => (
        <button
          key={value}
          type="button"
          className={`hero-switcher__btn${variant === value ? ' is-active' : ''}`}
          aria-pressed={variant === value}
          onClick={() => select(value)}
        >
          {value}
        </button>
      ))}
    </div>
  );
}

/* ---------------------------------- shared SVG --------------------------------- */

/* The Pipon mark is just three flat orange dots in the 2-up / 1-down triangle —
   no squircle, no plate, no background. Geometry measured from the 128px source
   logo: centres (46,47), (88,47), (67,85), radius 11.5. No gradients anywhere.
   The generous 128 viewBox keeps the dots floating on their field; the nav and
   footer use the cropped viewBox so the mark reads at 20px. */
function PipMark({
  size = 20,
  className = '',
  style,
  crop = false,
  tone = 'accent',
}) {
  const dot = tone === 'paper' ? '#FBF9F4' : '#E8532F';
  return (
    <svg
      className={className}
      style={{ width: size, height: size, ...style }}
      viewBox={crop ? '29 28 76 76' : '0 0 128 128'}
      aria-hidden="true"
      focusable="false"
    >
      <circle cx="46" cy="47" r="11.5" fill={dot} />
      <circle cx="88" cy="47" r="11.5" fill={dot} />
      <circle cx="67" cy="85" r="11.5" fill={dot} />
    </svg>
  );
}

const ArrowUpRight = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M7 17 17 7M8 7h9v9" />
  </svg>
);
const ArrowRight = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M5 12h14M12 5l7 7-7 7" />
  </svg>
);
const Heart = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8Z" />
  </svg>
);
const Reply = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.5 9 9 0 0 1-4-.9L3 21l1.9-5.5a9 9 0 0 1-.9-4A8.4 8.4 0 0 1 12.5 3 8.4 8.4 0 0 1 21 11.5Z" />
  </svg>
);
const ChevronDown = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="m6 9 6 6 6-6" />
  </svg>
);

/* ---------------------------------- video layer -------------------------------- */

function CinematicVideo({ src, poster, className }) {
  const ref = useRef(null);

  useEffect(() => {
    const video = ref.current;
    if (!video) return;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    video.muted = true;
    video.playsInline = true;
    video.src = src;

    const reveal = () => video.classList.add('is-ready');
    if (video.readyState >= 2) reveal();
    else video.addEventListener('loadeddata', reveal, { once: true });

    if (reduce) {
      video.removeAttribute('autoplay');
      video.pause();
      video.classList.add('is-ready');
    } else {
      video.play().catch(() => {});
    }

    const io = new IntersectionObserver(([entry]) => {
      if (reduce) return;
      if (entry.isIntersecting) video.play().catch(() => {});
      else video.pause();
    });
    io.observe(video);

    return () => {
      io.disconnect();
      video.removeEventListener('loadeddata', reveal);
      video.pause();
    };
  }, [src]);

  return (
    <video
      ref={ref}
      className={className}
      poster={poster}
      autoPlay
      muted
      loop
      playsInline
      preload="auto"
      aria-hidden="true"
    />
  );
}

/* ---------------------------------- hooks ------------------------------------- */

function useScrollReveals() {
  useEffect(() => {
    document.querySelectorAll('[data-stagger]').forEach((group) => {
      const step = Number(group.dataset.stagger) || 0;
      const base = Number(group.dataset.staggerBase) || 0;
      group.querySelectorAll('[data-reveal]').forEach((el, i) => {
        el.style.setProperty('--d', `${base + i * step}ms`);
      });
    });

    const elements = document.querySelectorAll('[data-reveal]');
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-in');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -10% 0px' }
    );
    elements.forEach((el) => io.observe(el));

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      elements.forEach((el) => el.classList.add('is-in'));
    }
    return () => io.disconnect();
  }, []);
}

/* ---------------------------------- nav --------------------------------------- */

function Nav() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const burgerRef = useRef(null);
  const menuRef = useRef(null);

  useEffect(() => {
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        setScrolled(window.scrollY > 60);
        ticking = false;
      });
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    const menu = menuRef.current;
    if (menu) menu.inert = !open;
    document.body.classList.toggle('menu-open', open);
    if (!open) return undefined;
    const onKey = (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
        burgerRef.current?.focus();
      }
    };
    const mq = window.matchMedia('(min-width: 768px)');
    const onChange = (event) => { if (event.matches) setOpen(false); };
    window.addEventListener('keydown', onKey);
    mq.addEventListener('change', onChange);
    return () => {
      window.removeEventListener('keydown', onKey);
      mq.removeEventListener('change', onChange);
    };
  }, [open]);

  useEffect(() => () => document.body.classList.remove('menu-open'), []);

  return (
    <>
      <header className={`nav${scrolled ? ' is-scrolled' : ''}`}>
        <a className="nav__logo" href="#top" aria-label="Pipon home">
          <PipMark size={22} crop className="nav__mark" />
          <span className="nav__word">pipon</span>
          <span className="nav__sup" aria-hidden="true" />
        </a>

        <nav className="nav__pill glass" aria-label="Primary">
          <a href="#explore">Explore</a>
          <a href="#how">How it works</a>
          <a href="#community">Community</a>
          <a className="nav__cta" href="#join">
            Join Pipon <ArrowUpRight width={14} height={14} />
          </a>
        </nav>

        <span className="nav__spacer" aria-hidden="true" />
        <button
          ref={burgerRef}
          className={`nav__burger${open ? ' is-open' : ''}`}
          aria-controls="mobile-menu"
          aria-expanded={open}
          aria-label={open ? 'Close menu' : 'Open menu'}
          onClick={() => setOpen((value) => !value)}
        >
          <span /><span /><span />
        </button>
      </header>

      <div className={`menu${open ? ' is-open' : ''}`} id="mobile-menu" ref={menuRef}>
        <nav className="menu__links" aria-label="Mobile">
          <a href="#explore" style={{ '--i': 0 }} onClick={() => setOpen(false)}>Explore</a>
          <a href="#pip" style={{ '--i': 1 }} onClick={() => setOpen(false)}>The Pip</a>
          <a href="#how" style={{ '--i': 2 }} onClick={() => setOpen(false)}>How it works</a>
          <a href="#community" style={{ '--i': 3 }} onClick={() => setOpen(false)}>Community</a>
          <a className="menu__cta" href="#join" style={{ '--i': 4 }} onClick={() => setOpen(false)}>
            Join Pipon <ArrowUpRight width={18} height={18} />
          </a>
        </nav>
      </div>
    </>
  );
}

/* ---------------------------------- hero -------------------------------------- */

function Hero({ variant }) {
  const portrait = usePortrait();
  const media = variant === 'brand'
    ? (portrait
        ? { src: '/pips-portrait.mp4', poster: '/pips-portrait-poster.jpg' }
        : { src: '/pips.mp4', poster: '/pips-poster.jpg' })
    : { src: '/spark.mp4', poster: '/spark-poster.jpg' };

  return (
    <section className={`hero hero--${variant}`} id="top">
      <div className="hero__media">
        <CinematicVideo
          key={media.src}
          src={media.src}
          poster={media.poster}
          className="hero__video"
        />
      </div>

      <div className="hero__copy">
        <div className="trust in-fade" style={{ '--d': '120ms' }}>
          <span className="trust__coin" style={{ background: WARM[4] }}>M</span>
          <span className="trust__coin" style={{ background: WARM[1] }}>A</span>
          <span className="trust__coin" style={{ background: WARM[0] }}>J</span>
          <span className="trust__pill">12k+ curious minds already here</span>
        </div>

        <p className="eyebrow in-blur" style={{ '--d': '180ms' }}>
          <span className="eyebrow__dot" aria-hidden="true" />A PLACE FOR SMALL THOUGHTS
        </p>

        <h1 className="hero__h1">
          <span className="hero__line in-blur" style={{ '--d': '280ms' }}>Share a thought.</span>
          <span className="hero__line in-blur" style={{ '--d': '400ms' }}>
            Find your <em>people.</em>
          </span>
        </h1>

        <p className="hero__sub in-fade" style={{ '--d': '560ms' }}>
          Pips are short posts for ideas, discoveries, works-in-progress and the odd 2am thought.
          Post one, wander through everyone else's, and see where the conversation goes.
        </p>

        <div className="hero__actions">
          <a className="btn-fill in-fade" style={{ '--d': '680ms' }} href="#join">
            <span>Join Pipon</span>
            <ArrowUpRight width={16} height={16} />
          </a>
          <a className="link-arrow in-fade" style={{ '--d': '760ms' }} href="#pip">
            <span className="link-arrow__disc"><ArrowRight width={13} height={13} /></span>
            See how it works
          </a>
        </div>
      </div>

      <span className="hero__strip in-fade" style={{ '--d': '860ms' }}>
        Scroll to meet a Pip <ChevronDown width={13} height={13} />
      </span>
    </section>
  );
}

/* ---------------------------------- marquee ----------------------------------- */

/* One accent, tonal variation only. No purple, teal or pink anywhere. */
const WARM = [
  'linear-gradient(135deg,#F2A65A,#E8532F)',
  'linear-gradient(135deg,#E8532F,#B03B1B)',
  'linear-gradient(135deg,#EFC3A4,#C65B26)',
  'linear-gradient(135deg,#B85C3C,#E8532F)',
  'linear-gradient(135deg,#F2C79B,#B85C3C)',
];

const FEED_POSTS = [
  { initial: 'N', text: 'Octopuses have three hearts. I need everyone to know.', tag: 'discoveries', grad: WARM[0] },
  { initial: 'L', text: "my sourdough finally rose and I'm weirdly emotional", tag: 'making', grad: WARM[3] },
  { initial: 'R', text: "What's a song that changed your mind about something?", tag: 'questions', grad: WARM[2] },
  { initial: 'T', text: "Sketching a logo for a friend's pottery studio", tag: 'creating', grad: WARM[4] },
  { initial: 'K', text: 'Why do the best ideas show up at 2am?', tag: 'thoughts', grad: WARM[1] },
  { initial: 'P', text: 'Made a tiny zine about the clouds in my city', tag: 'creating', grad: WARM[3] },
  { initial: 'E', text: 'Hot take: every library should have a nap corner', tag: 'thoughts', grad: WARM[0] },
  { initial: 'B', text: 'Learning to identify birds by sound. Today: a wren.', tag: 'discoveries', grad: WARM[2] },
  { initial: 'C', text: 'Three days into building a browser extension', tag: 'making', grad: WARM[1] },
  { initial: 'S', text: 'Someone left a note in a used book and it made my week', tag: 'thoughts', grad: WARM[4] },
];

function LiveMarquee() {
  const rootRef = useRef(null);
  const trackRef = useRef(null);
  const groupRef = useRef(null);

  useEffect(() => {
    const root = rootRef.current;
    const track = trackRef.current;
    const group = groupRef.current;
    if (!root || !track || !group) return undefined;

    const build = () => {
      if (!track.querySelector('.marquee__group[aria-hidden="true"]')) {
        const clone = group.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        track.appendChild(clone);
      }
      track.style.setProperty('--dur', `${(group.scrollWidth / 50).toFixed(2)}s`);
    };
    build();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(build);
    window.addEventListener('resize', build);
    return () => window.removeEventListener('resize', build);
  }, []);

  const chips = FEED_POSTS.map((post) => (
    <span className="mchip glass" key={post.text}>
      <span className="mchip__avatar" style={{ background: post.grad }}>{post.initial}</span>
      <span className="mchip__text">{post.text}</span>
      <span className="mchip__tag">#{post.tag}</span>
    </span>
  ));

  return (
    <section className="live" id="explore" aria-label="What's on Pipon right now">
      <div className="wrap live__head">
        <p className="eyebrow eyebrow--live">
          <span className="eyebrow__dot" aria-hidden="true" />RIGHT NOW ON PIPON
        </p>
      </div>
      <div className="marquee" ref={rootRef} data-speed="50">
        <div className="marquee__track" ref={trackRef}>
          <div className="marquee__group" ref={groupRef}>{chips}</div>
        </div>
      </div>
    </section>
  );
}

/* ---------------------------------- the pip ----------------------------------- */

const SMALL_PIPS = [
  {
    initial: 'D', name: 'Devon Park', handle: '@devon · 18m',
    grad: WARM[2],
    text: "Built a tiny browser extension that hides the word 'productivity' from my tabs. Highly recommend.",
    tag: '#making', likes: 46, replies: 9,
  },
  {
    initial: 'A', name: 'Ayo Bello', handle: '@ayo · 1h',
    grad: WARM[0],
    text: "Question: what's a small thing in your neighbourhood that makes you unreasonably happy?",
    tag: '#discoveries', likes: 212, replies: 63,
  },
  {
    initial: 'S', name: 'Sana Iqbal', handle: '@sana · 3h',
    grad: WARM[1],
    text: 'Day 4 of the linocut. The ink finally behaved.',
    tag: '#creating', likes: 88, replies: 12,
  },
];

function PipCardHeader({ initial, name, handle, grad, size = 'sm' }) {
  return (
    <div className="pip__head">
      <span className={`pip__avatar pip__avatar--${size}`} style={{ background: grad }}>{initial}</span>
      <span className="pip__who">
        <span className="pip__name">{name}</span>
        <span className="pip__handle">{handle}</span>
      </span>
    </div>
  );
}

function PipMeta({ tag, likes, replies }) {
  return (
    <div className="pip__meta">
      <span className="pip__tag">{tag}</span>
      <span className="pip__reactions">
        <span><Heart width={15} height={15} /> {likes}</span>
        <span><Reply width={15} height={15} /> {replies}</span>
      </span>
    </div>
  );
}

function PipShowcase() {
  return (
    <section className="pip-section" id="pip">
      <div className="wrap">
        <div className="pip-section__head">
          <div>
            <p className="eyebrow" data-reveal>01 / THE PIP</p>
            <h2 className="section-h2" data-reveal style={{ '--y': '40px', '--dur': '.85s' }}>
              Little posts.<br />Real <em>conversations.</em>
            </h2>
          </div>
          <p className="section-lede" data-reveal style={{ '--y': '24px', '--d': '140ms', '--dur': '.85s' }}>
            A Pip is short on purpose. No pressure to perform, no thread to win. Just one thing
            you want to say, and the people who want to hear it.
          </p>
        </div>

        <div className="showcase">
          <article className="pip pip--featured glass" data-reveal style={{ '--y': '50px', '--dur': '.9s' }}>
            <PipMark size={300} className="pip__watermark" />
            <PipCardHeader initial="M" name="Mira Okafor" handle="@mira · 2h" grad={WARM[3]} size="lg" />
            <p className="pip__quote">
              Finally put words to something I've felt for ages: the best conversations happen
              when nobody's trying to win.
            </p>
            <PipMeta tag="#thoughts" likes={128} replies={24} />
          </article>

          <div className="showcase__col" data-stagger="100" data-stagger-base="120">
            {SMALL_PIPS.map((pip) => (
              <article className="pip pip--small glass" key={pip.name} data-reveal>
                <PipCardHeader initial={pip.initial} name={pip.name} handle={pip.handle} grad={pip.grad} />
                <p className="pip__body">{pip.text}</p>
                <PipMeta tag={pip.tag} likes={pip.likes} replies={pip.replies} />
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ---------------------------------- many voices ------------------------------- */

function ThreadsSection() {
  return (
    <section className="voices" id="community">
      <div className="voices__media">
        <CinematicVideo src="/threads.mp4" poster="/threads-poster.jpg" className="voices__video" />
      </div>
      <div className="voices__inner">
        <div className="wrap voices__content">
          <p className="eyebrow eyebrow--mist" data-reveal>02 / THE NETWORK</p>
          <h2 className="voices__h2" data-reveal style={{ '--d': '120ms', '--y': '34px' }}>
            Many voices.<br />One <em>living</em> place.
          </h2>
          <p className="voices__body" data-reveal style={{ '--d': '240ms' }}>
            Every Pip is a thread. Follow one and it leads you to a person, a question,
            a whole new way of seeing something.
          </p>
          <p className="voices__stats" data-reveal style={{ '--d': '360ms' }}>
            12k+ curious minds <span>|</span> 40k Pips <span>|</span> 180 topics
          </p>
        </div>
      </div>
    </section>
  );
}

/* ---------------------------------- how it works ------------------------------ */

const STEPS = [
  {
    n: '01', title: 'Post a thought',
    body: 'A sentence, a sketch, a half-formed question. Short is the whole point.',
    detail: 'A line or two is plenty. No cover image, no hook, no seven-part thread.',
  },
  {
    n: '02', title: 'Follow the thread',
    body: 'Wander through Pips by topic, not by follower count. Curiosity does the sorting.',
    detail: 'Topics are made by the people posting, not by a trending page.',
  },
  {
    n: '03', title: 'Find your people',
    body: 'Reply, build on an idea, or just sit with it. Conversations start small here.',
    detail: 'No follower counts on display. Replies appear in the order they arrived.',
  },
];

function Steps() {
  const [openStep, setOpenStep] = useState(null);

  return (
    <section className="steps" id="how">
      <div className="wrap steps__grid">
        <div className="steps__intro">
          <p className="eyebrow" data-reveal>03 / HOW IT WORKS</p>
          <h2 className="section-h2" data-reveal style={{ '--d': '100ms', '--y': '34px' }}>
            Three steps to<br />your first <em>Pip.</em>
          </h2>
          <p className="steps__note" data-reveal style={{ '--d': '200ms' }}>No profile optimisation required.</p>
        </div>
        <div className="steps__rows" data-stagger="120" data-stagger-base="100">
          {STEPS.map((step, i) => {
            const isOpen = openStep === i;
            return (
              <div className={`step${isOpen ? ' is-open' : ''}`} key={step.n} data-reveal>
                <button
                  type="button"
                  className="step__toggle"
                  aria-expanded={isOpen}
                  aria-controls={`step-panel-${i}`}
                  onClick={() => setOpenStep(isOpen ? null : i)}
                >
                  <span className="step__n">{step.n}</span>
                  <span className="step__text">
                    <span className="step__title">{step.title}</span>
                    <span className="step__body">{step.body}</span>
                  </span>
                  <ChevronDown className="step__chev" width={18} height={18} />
                </button>
                <div className="step__panel" id={`step-panel-${i}`} hidden={!isOpen}>
                  <p>{step.detail}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/* ---------------------------------- join + footer ----------------------------- */

function JoinCTA() {
  const [email, setEmail] = useState('');
  const [joined, setJoined] = useState(false);

  return (
    <section className="join" id="join">
      <PipMark size={520} className="join__watermark" />
      <div className="wrap join__inner">
        <p className="eyebrow eyebrow--light" data-reveal>COMING SOON</p>
        <h2 className="join__h2" data-reveal style={{ '--d': '100ms', '--y': '34px' }}>
          Your next thought<br />belongs <em>here.</em>
        </h2>
        <p className="join__sub" data-reveal style={{ '--d': '200ms' }}>
          No algorithms shouting. Just people, and the things they're thinking about.
        </p>

        <div className="join__form" data-reveal style={{ '--d': '300ms' }}>
          {joined ? (
            <p className="join__done" role="status">You're on the list. We'll be in touch.</p>
          ) : (
            <form
              className="email-pill"
              onSubmit={(event) => { event.preventDefault(); setJoined(true); }}
            >
              <input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@somewhere.com"
                aria-label="Email address"
              />
              <button type="submit">Get early access</button>
            </form>
          )}
          <p className="join__fine">Free to join. No spam, ever.</p>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  const columns = [
    { title: 'Product', links: [['Explore', '#explore'], ['Pips', '#pip'], ['Topics', '#community']] },
    { title: 'Company', links: [['About', '#community'], ['Journal', '#pip'], ['Careers', '#join']] },
    { title: 'Elsewhere', links: [['Instagram', '#join'], ['Are.na', '#join'], ['Email', '#join']] },
  ];
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer__top">
          <a className="footer__logo" href="#top" aria-label="Pipon home">
            <PipMark size={22} crop />
            <span>pipon</span>
          </a>
          <div className="footer__cols">
            {columns.map((col) => (
              <div className="footer__col" key={col.title}>
                <p className="footer__title">{col.title}</p>
                {col.links.map(([label, href]) => <a href={href} key={label}>{label}</a>)}
              </div>
            ))}
          </div>
        </div>
        <div className="footer__bottom">
          <span>© 2026 Pipon</span>
          <span>Made for small thoughts.</span>
        </div>
      </div>
    </footer>
  );
}

/* ---------------------------------- app --------------------------------------- */

export default function App() {
  useScrollReveals();
  const { variant, compare, select } = useHeroVariant();

  return (
    <>
      <div className="page-grain" aria-hidden="true" />
      <Nav />
      <main>
        <Hero variant={variant} />
        <LiveMarquee />
        <PipShowcase />
        <ThreadsSection />
        <Steps />
        <JoinCTA />
      </main>
      <Footer />
      {compare && <HeroSwitcher variant={variant} select={select} />}
    </>
  );
}
