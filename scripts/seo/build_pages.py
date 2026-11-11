#!/usr/bin/env python3
"""Generates the TutorMate marketing pages from one shared shell.

Keeping nav, footer, and the publisher schema in a single place means they
cannot drift apart across pages, which is what produced the inconsistent
branding and the missing metadata the SEO audit picked up.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
WWW = ROOT / "www"
SITE = "https://tutormate.ai"
# Verified listing id 6793738685. No Apple provider token (pt) is in this repo,
# so campaign parameters are intentionally absent. See docs/analytics/app-store-clicks.md.
APP_STORE = "https://apps.apple.com/app/id6793738685"

IOS_HEAD_SCRIPT = """    <script>
        (function () {
            var ua = navigator.userAgent || "";
            var iOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
            var native = window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform();
            if (iOS && !native) document.documentElement.classList.add("is-ios");
        })();
    </script>
"""

IOS_BAR = f"""    <div id="ios-download-bar" hidden>
        <div class="ios-bar-inner">
            <p class="ios-bar-title">For iPhone and iPad</p>
            <a href="{APP_STORE}" data-placement="ios-sticky" class="ios-bar-btn">Get the app</a>
            <a href="/app/" class="ios-bar-browser">Browser</a>
            <button type="button" id="ios-download-dismiss" aria-label="Dismiss the App Store suggestion">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    </div>
"""

PUBLISHER = {
    "@type": "Organization",
    "@id": f"{SITE}/#publisher",
    "name": "Walker Intelligence Group",
    "url": "https://walkerig.com/",
    "email": "support@tutormate.ai",
    "founder": {"@type": "Person", "name": "Dustin Michael Walker"},
}

NAV = f"""    <nav class="w-full bg-navy-800 shadow-md sticky top-0 z-50">
        <div class="w-full flex justify-between items-center max-w-5xl mx-auto px-4 h-16">
            <a href="/" class="flex items-center gap-2">
                <img src="/Assets/TutorMateLogoTransparent.png" alt="TutorMate" width="221" height="199" class="h-9 w-9 brightness-0 invert">
                <span class="nav-brand-text text-white font-title text-lg">TutorMate</span>
            </a>
            <div class="flex items-center gap-3 sm:gap-5">
                <a href="/homework-help/" class="hidden md:inline text-white/80 hover:text-white text-sm font-medium">Homework help</a>
                <a href="/quiz-generator/" class="hidden md:inline text-white/80 hover:text-white text-sm font-medium">Quiz generator</a>
                <a href="/#faq" class="hidden sm:inline text-white/80 hover:text-white text-sm font-medium">FAQ</a>
                <a href="/#pricing" class="hidden sm:inline text-white/80 hover:text-white text-sm font-medium">Pricing</a>
                <a href="/app/" class="nav-browser-text text-white/80 hover:text-white text-sm font-medium">In browser</a>
                <a href="{APP_STORE}" data-placement="nav" aria-label="Download TutorMate for iPhone and iPad" class="nav-ios px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-navy-900 bg-white hover:bg-slate-100 transition-all">
                    Get the iOS app
                </a>
            </div>
        </div>
    </nav>
"""

FOOTER = """    <footer class="bg-navy-900 mt-16">
        <div class="max-w-5xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p class="text-xs text-navy-200">
                &copy; 2026 TutorMate, a product of Walker Intelligence Group. All rights reserved.
            </p>
            <div class="flex flex-wrap justify-center gap-5 text-xs text-navy-200">
                <a href="/about/" class="hover:text-white">About</a>
                <a href="/homework-help/" class="hover:text-white">Homework help</a>
                <a href="/quiz-generator/" class="hover:text-white">Quiz generator</a>
                <a href="/algebra/" class="hover:text-white">Algebra</a>
                <a href="/biology/" class="hover:text-white">Biology</a>
                <a href="/written-answers/" class="hover:text-white">Written answers</a>
                <a href="/vs/photomath/" class="hover:text-white">vs Photomath</a>
                <a href="/privacy/" class="hover:text-white">Privacy Policy</a>
                <a href="mailto:support@tutormate.ai" class="hover:text-white">Support</a>
            </div>
        </div>
    </footer>
"""

CTA = f"""    <section id="download" class="max-w-3xl mx-auto px-6 py-12 text-center">
        <div class="rounded-2xl bg-navy-800 px-6 py-10">
            <h2 class="font-title text-2xl text-white">Try it on your next assignment</h2>
            <p class="mt-3 text-navy-50 max-w-lg mx-auto">
                Your first 10 assignment checks and quizzes are free. No credit card needed to start.
            </p>
            <div class="cta-row text-white mt-7">
                <a href="{APP_STORE}" data-cta="ios" data-placement="section" class="btn-cta btn-store">
                    Download for iPhone and iPad
                </a>
                <a href="/app/" data-cta="browser" class="btn-cta btn-browser">
                    Use it in the browser
                </a>
            </div>
            <p class="cta-note mt-3 text-navy-200 text-xs">The download is the iPhone and iPad app. A Mac, PC, or Android phone can use the browser.</p>
        </div>
    </section>
"""


def breadcrumbs(trail):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": SITE + path}
            for i, (name, path) in enumerate(trail, start=1)
        ],
    }


def page(path, title, description, slug_schema, body, trail):
    url = f"{SITE}{path}"
    graph = {"@context": "https://schema.org", "@graph": [PUBLISHER, breadcrumbs(trail)] + slug_schema}
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{url}">
    <meta name="theme-color" content="#1B2447">

    <!-- Smart App Banner: turns iPhone web visitors into attributed App Store
         installs. Apple reports these as a distinct source in App Analytics. -->
    <meta name="apple-itunes-app" content="app-id=6793738685">
{IOS_HEAD_SCRIPT}
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="TutorMate">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{SITE}/Assets/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{SITE}/Assets/og-image.png">

    <link rel="icon" type="image/png" href="/Assets/TutorMateLogoTransparent.png">
    <link rel="apple-touch-icon" href="/Assets/TutorMateLogoTransparent.png">
    <link rel="preload" href="/fonts/nunito-800.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="/styles/tailwind.5130087d.css">
</head>
<body class="bg-slate-50 text-slate-800 antialiased">

{NAV}
{body}
{CTA}
{FOOTER}
{IOS_BAR}
    <script src="/scripts/store-cta.js" defer></script>
    <script type="application/ld+json">
{json.dumps(graph, indent=2, ensure_ascii=False)}
    </script>

</body>
</html>
"""
    out = WWW / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"wrote {out.relative_to(ROOT)}  ({len(html):,} bytes)")


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------
page(
    "/about/",
    "About TutorMate | Who Makes the AI Homework Checker",
    "TutorMate is an AI homework checker from Walker Intelligence Group. Who builds it, why it checks work instead of answering it, and what it is not.",
    [{
        "@type": "AboutPage",
        "@id": f"{SITE}/about/#page",
        "name": "About TutorMate",
        "url": f"{SITE}/about/",
        "publisher": {"@id": f"{SITE}/#publisher"},
        "mainEntity": {"@id": f"{SITE}/#app"},
    }],
    """    <main class="max-w-3xl mx-auto px-6 py-14">
        <h1 class="font-title text-3xl text-navy-900">About TutorMate</h1>

        <p class="mt-6 text-lg text-slate-700 leading-relaxed">
            TutorMate is an AI study app that checks homework you have already done and explains the
            reasoning behind each answer, and that turns any worksheet, topic, or set of notes into a
            custom practice quiz. It runs in the browser at tutormate.ai and as a native app for iPhone
            and iPad.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Who makes TutorMate</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            TutorMate is built by <strong>Walker Intelligence Group</strong>, an independent software
            studio that builds AI products. The iOS app is published on the Apple App Store by
            <strong>Dustin Michael Walker</strong>, the studio's founder. TutorMate is not affiliated with
            any school, school district, examination board, or tutoring charity, and it is not funded by
            one. It is a paid consumer product with a free tier, and the subscription revenue is the only
            way it makes money. Nobody pays to have content placed in it, and student work is never sold
            or used for advertising.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            You can reach a human about anything at
            <a href="mailto:support@tutormate.ai" class="text-navy-700 underline">support@tutormate.ai</a>.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Not the Chapter One reading program</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            The name TutorMate is shared with an unrelated and much older project. <em>TutorMate</em> is
            also the name of a volunteer early-literacy reading program for children in the first years
            of elementary school, run by the nonprofit Chapter One, formerly Innovations for Learning. That
            program pairs corporate volunteers with young readers and has been running since the 1990s.
            It has nothing to do with this product.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            If you were looking for the volunteer reading program, you want Chapter One, not this site.
            This TutorMate is the AI homework-checking and quiz-generating app at tutormate.ai, first
            released in August 2026.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Why it checks work instead of doing it</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Most AI homework tools are solvers. You photograph a question you have not attempted and the
            app returns the finished answer. That is genuinely useful when you are stuck, and genuinely
            corrosive when it becomes the default, because the student never finds out which parts of the
            method they had actually understood.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            TutorMate is built the other way round. The core workflow assumes you have already attempted
            the work. You photograph the page you filled in, and TutorMate goes through it answer by
            answer: this one is right, this one is wrong, and here is the reasoning. The information you
            get back is diagnostic rather than substitutive. It tells you where your understanding broke
            down, which is the thing a tutor would tell you and the thing a solver cannot.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            The quiz generator follows from the same principle. Instead of answering your questions, it
            asks you questions, built from the material you are actually studying, so that review
            involves retrieval rather than re-reading. This is a deliberate product constraint, not a
            limitation we intend to remove.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">How it works under the hood</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Images and text you submit are sent over an encrypted connection to TutorMate's own server and
            processed by Google's Gemini API, which handles the reading of the page and the generation of
            the feedback or quiz. Accounts, saved folders, and uploaded files are stored in Google
            Firebase. Subscriptions are handled by Apple in the iOS app and by Stripe on the web, so
            TutorMate never sees or stores your payment details.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            You can delete individual saved items at any time, and you can permanently delete your entire
            account, including every uploaded image, from the app menu. The
            <a href="/privacy/" class="text-navy-700 underline">privacy policy</a> describes all of this in
            detail, including what is collected and what is not.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">What it costs</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Your first 10 assignment checks and quizzes are free and need no credit card. After that,
            TutorMate costs $4.95 per month or $49 per year, and the price is identical on the web and on
            iOS. You can cancel at any time.
        </p>
    </main>
""",
    [("TutorMate", "/"), ("About", "/about/")],
)


# ---------------------------------------------------------------------------
# Homework help (use case / money page)
# ---------------------------------------------------------------------------
_HOMEWORK_FAQ = [
    ("Can AI check my homework for free?",
     "Yes. TutorMate gives you 10 free assignment checks with no credit card required. Photograph the "
     "finished page and it marks each answer and explains the reasoning. After the first 10, unlimited "
     "checking costs $4.95 per month or $49 per year."),
    ("Will my teacher know I used TutorMate?",
     "TutorMate does not alter your work or write anything for you, so there is nothing added to your "
     "assignment to detect. You submit your own answers in your own handwriting. What TutorMate gives "
     "you is feedback on work you have already done, which is the same thing a parent, a tutor, or a "
     "study group would give you."),
    ("Does TutorMate work for subjects other than math?",
     "Yes. Because TutorMate reads the page and reasons about the answers rather than running a math "
     "solver, it is not limited to numerical work. It handles written answers, definitions, "
     "short-answer questions, and problem sets. Math-only solvers cannot check a history or biology "
     "worksheet; TutorMate can."),
]

page(
    "/homework-help/",
    "AI Homework Help That Checks Your Answers | TutorMate",
    "AI homework help that checks answers you worked out yourself. Photograph a finished worksheet, handwritten or printed, and see what is wrong and why.",
    [
        {
            "@type": "WebPage",
            "@id": f"{SITE}/homework-help/#page",
            "name": "AI homework help that checks your answers",
            "url": f"{SITE}/homework-help/",
            "publisher": {"@id": f"{SITE}/#publisher"},
            "about": {"@id": f"{SITE}/#app"},
        },
        {
            "@type": "HowTo",
            "@id": f"{SITE}/homework-help/#howto",
            "name": "How to check your homework with TutorMate",
            "totalTime": "PT2M",
            "step": [
                {"@type": "HowToStep", "position": 1, "name": "Finish the assignment",
                 "text": "Complete the worksheet or problem set yourself, by hand or on screen."},
                {"@type": "HowToStep", "position": 2, "name": "Photograph the page",
                 "text": "Open TutorMate on the web or on iPhone and photograph the whole page in good light, or upload an existing image or file."},
                {"@type": "HowToStep", "position": 3, "name": "Read the answer-by-answer feedback",
                 "text": "TutorMate marks each answer right or wrong and explains the reasoning behind it, so you can see where your method went wrong."},
                {"@type": "HowToStep", "position": 4, "name": "Practice the parts you got wrong",
                 "text": "Generate a practice quiz on the topics you missed and save it to a folder to revisit before the test."},
            ],
        },
        {
            "@type": "FAQPage",
            "@id": f"{SITE}/homework-help/#faq",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in _HOMEWORK_FAQ
            ],
        },
    ],
    """    <main class="max-w-3xl mx-auto px-6 py-14">
        <nav aria-label="Breadcrumb" class="text-xs text-slate-500">
            <a href="/" class="hover:text-navy-700 underline">TutorMate</a>
            <span class="mx-1">/</span>
            <span>Homework help</span>
        </nav>

        <h1 class="font-title text-3xl text-navy-900 mt-4">AI homework help that checks your answers</h1>

        <p class="mt-6 text-lg text-slate-700 leading-relaxed">
            Most AI homework help gives you the answer. TutorMate checks the answer you worked out
            yourself. You finish the assignment, photograph the page, and TutorMate goes through it one
            question at a time: what is right, what is wrong, and the reasoning behind each verdict. Your
            first 10 checks are free.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Why checking beats solving</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            When you are stuck on a problem, a solver is a shortcut to the end of the problem. It is not a
            shortcut to understanding it. You copy the worked solution, the assignment gets finished, and
            the gap in your method survives untouched until it resurfaces in the test, where no solver is
            available.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Checking works the other way. Because you committed to an answer first, the feedback is
            specific to the way <em>you</em> approached the problem. If you dropped a negative sign in step
            three, that is what you find out. If you used the right method on the wrong quantity, that is
            what you find out. This is diagnostic information about your own understanding, and it is the
            thing that actually changes your score next time.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">How to check your homework</h2>
        <ol class="mt-4 space-y-4 text-slate-600 leading-relaxed list-decimal list-inside">
            <li><strong class="text-slate-900">Finish the work yourself.</strong> By hand on paper, or on screen. TutorMate is built for completed work.</li>
            <li><strong class="text-slate-900">Photograph the page.</strong> Open TutorMate in your browser or on your iPhone and take a photo of the whole page in good light. You can also upload an image or a document you already have.</li>
            <li><strong class="text-slate-900">Read the feedback.</strong> Each answer comes back marked, with the reasoning spelled out rather than just a tick or a cross.</li>
            <li><strong class="text-slate-900">Practice what you missed.</strong> Turn the topics you got wrong into a quiz and save it to a folder for review before the test.</li>
        </ol>

        <h2 class="font-title text-2xl text-navy-900 mt-12">It reads handwriting</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Homework is mostly handwritten, so a tool that only reads typed text is not much use. TutorMate
            reads handwritten answers as well as printed worksheets. Photograph the page you filled in by
            hand and it works through your actual writing. Clear, well-lit photographs of the whole page
            give the most reliable results. Dense or heavily annotated worksheets take longer to process
            than simple ones, because there is more on the page to read.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Not just math</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Math solvers are narrow by construction: they parse an equation and run it. TutorMate reads
            the page and reasons about what is on it, so it is not restricted to numerical work. It handles
            written answers, definitions, short-answer questions, vocabulary, and mixed problem sets
            alongside math.             A solver cannot check a biology worksheet or a set of history short answers.
            This can. See the worked examples for
            <a href="/algebra/" class="text-navy-700 underline">algebra</a>,
            <a href="/biology/" class="text-navy-700 underline">biology</a>, and
            <a href="/written-answers/" class="text-navy-700 underline">short written answers</a>.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Is this cheating?</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            No, and the distinction is structural rather than a matter of good intentions. TutorMate will
            not produce an assignment for you. The workflow requires a completed attempt as its input, so
            the work on the page is yours. Getting feedback on finished work is what happens when a parent
            looks over your math, when a study group compares answers, or when a teacher hands back a
            graded paper. What schools object to is submitting work you did not do, and TutorMate does not
            produce work to submit.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Common questions</h2>
        <div class="mt-6 space-y-8">
            <div>
                <h3 class="font-semibold text-navy-900">Can AI check my homework for free?</h3>
                <p class="mt-2 text-slate-600 leading-relaxed">
                    Yes. TutorMate gives you 10 free assignment checks with no credit card required.
                    Photograph the finished page and it marks each answer and explains the reasoning. After
                    the first 10, unlimited checking costs $4.95 per month or $49 per year.
                </p>
            </div>
            <div>
                <h3 class="font-semibold text-navy-900">Will my teacher know I used TutorMate?</h3>
                <p class="mt-2 text-slate-600 leading-relaxed">
                    TutorMate does not alter your work or write anything for you, so there is nothing added
                    to your assignment to detect. You submit your own answers in your own handwriting. What
                    TutorMate gives you is feedback on work you have already done, which is the same thing
                    a parent, a tutor, or a study group would give you.
                </p>
            </div>
            <div>
                <h3 class="font-semibold text-navy-900">Does TutorMate work for subjects other than math?</h3>
                <p class="mt-2 text-slate-600 leading-relaxed">
                    Yes. Because TutorMate reads the page and reasons about the answers rather than running
                    a math solver, it is not limited to numerical work. It handles written answers,
                    definitions, short-answer questions, and problem sets. Math-only solvers cannot check
                    a history or biology worksheet; TutorMate can.
                </p>
            </div>
        </div>
    </main>
""",
    [("TutorMate", "/"), ("Homework help", "/homework-help/")],
)


# ---------------------------------------------------------------------------
# Quiz generator (use case / money page)
# ---------------------------------------------------------------------------
page(
    "/quiz-generator/",
    "Turn Any Worksheet Into a Practice Quiz | TutorMate",
    "Photograph a worksheet, paste your notes, or type a topic, and TutorMate builds a custom practice quiz in seconds. Save it and retake it before the test.",
    [
        {
            "@type": "WebPage",
            "@id": f"{SITE}/quiz-generator/#page",
            "name": "AI practice quiz generator",
            "url": f"{SITE}/quiz-generator/",
            "publisher": {"@id": f"{SITE}/#publisher"},
            "about": {"@id": f"{SITE}/#app"},
        },
        {
            "@type": "HowTo",
            "@id": f"{SITE}/quiz-generator/#howto",
            "name": "How to turn a worksheet or topic into a practice quiz",
            "totalTime": "PT1M",
            "step": [
                {"@type": "HowToStep", "position": 1, "name": "Give TutorMate the material",
                 "text": "Photograph a worksheet or study sheet, upload a document, paste your notes, or simply type the topic you need to review."},
                {"@type": "HowToStep", "position": 2, "name": "Generate the quiz",
                 "text": "TutorMate builds a set of practice questions from that material in seconds."},
                {"@type": "HowToStep", "position": 3, "name": "Take it and check your score",
                 "text": "Answer the questions and see which ones you got wrong, with the reasoning explained."},
                {"@type": "HowToStep", "position": 4, "name": "Save it and retake it",
                 "text": "Store the quiz in a folder so you can retake it closer to the test, on the web or on your phone."},
            ],
        },
    ],
    """    <main class="max-w-3xl mx-auto px-6 py-14">
        <nav aria-label="Breadcrumb" class="text-xs text-slate-500">
            <a href="/" class="hover:text-navy-700 underline">TutorMate</a>
            <span class="mx-1">/</span>
            <span>Quiz generator</span>
        </nav>

        <h1 class="font-title text-3xl text-navy-900 mt-4">Turn any worksheet into a practice quiz</h1>

        <p class="mt-6 text-lg text-slate-700 leading-relaxed">
            Photograph a worksheet, upload your notes, or just type a topic, and TutorMate builds a
            custom practice quiz from it in seconds. Take it, see what you missed, save it to a folder,
            and retake it the night before the test. Your first 10 quizzes are free.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Why self-testing beats re-reading</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Re-reading notes feels productive because the material gets easier to recognize each time. That
            feeling is the problem: recognition is not recall, and the test asks for recall. Being asked a
            question you have to retrieve the answer to is harder, feels worse, and works better. This is
            one of the most consistently reproduced findings in the study-strategy literature, usually
            called the testing effect or retrieval practice.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            The practical obstacle has always been that somebody has to write the questions. Textbook
            questions run out, and writing your own means knowing the answers already. That is the part
            TutorMate automates: it generates the questions, from your material, so the work you put in
            goes into answering them.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Four ways to start a quiz</h2>
        <ul class="mt-4 space-y-4 text-slate-600 leading-relaxed">
            <li><strong class="text-slate-900">Photograph a worksheet.</strong> Point your camera at a study sheet, a textbook page, or a worksheet you have been given, and get questions drawn from it.</li>
            <li><strong class="text-slate-900">Upload a document.</strong> Feed it the handout or notes file you already have.</li>
            <li><strong class="text-slate-900">Paste your notes.</strong> Drop in the notes you took in class and review from what your teacher actually emphasized.</li>
            <li><strong class="text-slate-900">Type a topic.</strong> No material to hand? Type the subject, such as the causes of the French Revolution, balancing chemical equations, or <a href="/biology/" class="text-navy-700 underline">10th grade photosynthesis</a>, and get a quiz on it.</li>
        </ul>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Quizzes from your material, not a generic bank</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            A pre-made question bank tests the subject in general. Your test does not: it tests the
            specific material your teacher covered, with their emphasis and their vocabulary. Because
            TutorMate generates questions from the worksheet or notes you give it, the practice stays
            aligned to what you will actually be examined on. If your class spent two weeks on one topic
            and skipped another, a quiz built from your own notes reflects that.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Save it, then retake it</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Quizzes are saved into folders, so the work does not evaporate the moment you close the app.
            Keep a folder per subject or per unit, and come back to the same quiz a few days later, which
            is roughly when spaced repetition says it will do the most good. Folders sync between the web
            app and the iOS app, so you can build a quiz on a laptop and retake it on your phone on the
            bus.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">It pairs with homework checking</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            The two halves of TutorMate are designed to feed each other. Use
            <a href="/homework-help/" class="text-navy-700 underline">homework checking</a> to find out
            which questions you got wrong and why, then generate a quiz on exactly those topics. That loop,
            from attempt to diagnosis to targeted practice, is what a tutor does with you in an hour, and
            it is the reason the app does both jobs rather than one.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">What it costs</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Your first 10 quizzes and assignment checks are free, with no credit card. Unlimited use is
            $4.95 per month or $49 per year, the same price on the web and on iOS, and you can cancel at any
            time.
        </p>
    </main>
""",
    [("TutorMate", "/"), ("Quiz generator", "/quiz-generator/")],
)


# ---------------------------------------------------------------------------
# Comparison: vs Photomath
#
# Deliberately no price claim for Photomath. Public sources disagree on the
# current Plus price, and a wrong competitor price is worse than no price.
# ---------------------------------------------------------------------------
page(
    "/vs/photomath/",
    "TutorMate vs Photomath: Checker or Solver? | TutorMate",
    "Photomath solves math problems. TutorMate checks answers you worked out yourself, across any subject, and builds practice quizzes. An honest comparison.",
    [
        {
            "@type": "WebPage",
            "@id": f"{SITE}/vs/photomath/#page",
            "name": "TutorMate vs Photomath",
            "url": f"{SITE}/vs/photomath/",
            "publisher": {"@id": f"{SITE}/#publisher"},
            "about": {"@id": f"{SITE}/#app"},
        },
        {
            "@type": "FAQPage",
            "@id": f"{SITE}/vs/photomath/#faq",
            "mainEntity": [
                {"@type": "Question",
                 "name": "Is TutorMate a Photomath alternative?",
                 "acceptedAnswer": {"@type": "Answer", "text":
                    "Partly. If you want a math problem solved step by step, Photomath does that job "
                    "better because it is purpose-built for it. If what you want is to find out whether "
                    "the answers you worked out yourself are correct, across any subject rather than "
                    "only math, then TutorMate does something Photomath does not do at all."}},
                {"@type": "Question",
                 "name": "Can I use both Photomath and TutorMate?",
                 "acceptedAnswer": {"@type": "Answer", "text":
                    "Yes, and they do not overlap much. Photomath is useful when you are stuck mid-problem "
                    "and need to see the method. TutorMate is useful after you have finished, to verify "
                    "your answers and to generate practice questions before a test."}},
                {"@type": "Question",
                 "name": "Which is better for parents checking a child's homework?",
                 "acceptedAnswer": {"@type": "Answer", "text":
                    "TutorMate, because checking is the whole workflow. A parent can photograph the "
                    "finished page and see which answers are wrong and why, without needing to know the "
                    "subject themselves. A solver requires re-entering each unanswered question and does "
                    "not evaluate what the child actually wrote."}},
            ],
        },
    ],
    """    <main class="max-w-3xl mx-auto px-6 py-14">
        <nav aria-label="Breadcrumb" class="text-xs text-slate-500">
            <a href="/" class="hover:text-navy-700 underline">TutorMate</a>
            <span class="mx-1">/</span>
            <span>vs Photomath</span>
        </nav>

        <h1 class="font-title text-3xl text-navy-900 mt-4">TutorMate vs Photomath</h1>

        <p class="mt-6 text-lg text-slate-700 leading-relaxed">
            These two apps are often compared, but they are built for opposite moments in the homework
            process. Photomath is a solver: you photograph a problem you have not answered and it shows you
            how to answer it. TutorMate is a checker: you photograph work you have already finished and it
            tells you whether you got it right and why. Which one you want depends on whether you are
            stuck or done.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">The short version</h2>
        <div class="mt-6 overflow-x-auto">
            <table class="w-full text-sm text-left border-collapse">
                <thead>
                    <tr class="border-b-2 border-slate-300">
                        <th scope="col" class="py-3 pr-4 font-semibold text-slate-900"></th>
                        <th scope="col" class="py-3 pr-4 font-semibold text-navy-900">TutorMate</th>
                        <th scope="col" class="py-3 font-semibold text-slate-900">Photomath</th>
                    </tr>
                </thead>
                <tbody class="text-slate-600">
                    <tr class="border-b border-slate-200">
                        <th scope="row" class="py-3 pr-4 font-medium text-slate-900">Core job</th>
                        <td class="py-3 pr-4">Checks answers you wrote</td>
                        <td class="py-3">Solves problems for you</td>
                    </tr>
                    <tr class="border-b border-slate-200">
                        <th scope="row" class="py-3 pr-4 font-medium text-slate-900">Subjects</th>
                        <td class="py-3 pr-4">Any subject, including written answers</td>
                        <td class="py-3">Math</td>
                    </tr>
                    <tr class="border-b border-slate-200">
                        <th scope="row" class="py-3 pr-4 font-medium text-slate-900">Reads your handwriting</th>
                        <td class="py-3 pr-4">Yes, your filled-in answers</td>
                        <td class="py-3">Reads the printed or written problem</td>
                    </tr>
                    <tr class="border-b border-slate-200">
                        <th scope="row" class="py-3 pr-4 font-medium text-slate-900">Practice quizzes</th>
                        <td class="py-3 pr-4">Yes, generated from your material</td>
                        <td class="py-3">No</td>
                    </tr>
                    <tr class="border-b border-slate-200">
                        <th scope="row" class="py-3 pr-4 font-medium text-slate-900">Step-by-step solutions</th>
                        <td class="py-3 pr-4">Explains the reasoning for your answer</td>
                        <td class="py-3">Yes, its main strength</td>
                    </tr>
                    <tr class="border-b border-slate-200">
                        <th scope="row" class="py-3 pr-4 font-medium text-slate-900">Platforms</th>
                        <td class="py-3 pr-4">Web and iOS</td>
                        <td class="py-3">iOS and Android</td>
                    </tr>
                    <tr class="border-b border-slate-200">
                        <th scope="row" class="py-3 pr-4 font-medium text-slate-900">Price</th>
                        <td class="py-3 pr-4">10 free, then $4.95/mo or $49/yr</td>
                        <td class="py-3">Free tier plus a paid Plus tier</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p class="mt-4 text-xs text-slate-500">
            Photomath's current subscription price is not listed here because public sources disagree on
            it. Check the App Store or Play Store listing for the authoritative figure.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">What Photomath does better</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Photomath has been doing one thing since 2014 and does it very well. It recognizes a math
            expression from a photograph and walks through the solution method step by step, with the
            algebra laid out. It is now developed by Google. For a student who is genuinely stuck halfway
            through a problem and needs to see how the next move works, that is the right tool, and a
            general-purpose checker is not a substitute for it.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            It also covers Android, which TutorMate does not have a native app for, and it has a free tier
            that handles a large share of ordinary math problems.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">What TutorMate does that Photomath does not</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            <strong class="text-slate-900">It evaluates your work rather than replacing it.</strong>
            Photomath has no opinion about the answer you wrote, because it never sees it. You give it the
            question, not your attempt. TutorMate's input is the completed page, so the feedback is about
            your reasoning: which answers are wrong, and what went wrong in getting there.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            <strong class="text-slate-900">It is not restricted to math.</strong> A math solver cannot do
            anything with a biology worksheet, a set of history short answers, or a vocabulary exercise.
            Because TutorMate reads the page and reasons about the content, it handles
            <a href="/written-answers/" class="text-navy-700 underline">written answers</a> and
            definitions alongside <a href="/algebra/" class="text-navy-700 underline">numerical work</a>.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            <strong class="text-slate-900">It generates practice.</strong> TutorMate turns a worksheet,
            your notes, or a typed topic into a
            <a href="/quiz-generator/" class="text-navy-700 underline">custom practice quiz</a>, which is
            the part that actually prepares you for a test. Solvers do not do this.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">The cheating question</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            This is the honest difference between the two categories, and it is worth being direct about.
            A solver can be used well, as a worked example when you are stuck, or badly, as a way to
            produce answers you do not understand. Which one happens depends entirely on the student's
            discipline, because the tool permits both.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            A checker constrains the choice. TutorMate cannot produce an assignment for you, because it
            needs your completed attempt before it can do anything at all. That is why parents tend to be
            comfortable with checking and uneasy about solving: it is not a difference in marketing, it is
            a difference in what the software will physically do.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Which should you use?</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            If your work is almost entirely math and your main problem is getting unstuck mid-problem,
            use Photomath. If your problem is not knowing whether your finished homework is right, if your
            subjects go beyond math, or if you want practice questions before a test, use TutorMate. Plenty
            of students have a reason to use both, and they do not really compete for the same moment in
            the evening.
        </p>
    </main>
""",
    [("TutorMate", "/"), ("vs Photomath", "/vs/photomath/")],
)


import guide_pages

guide_pages.add_guide_pages(page, SITE)
