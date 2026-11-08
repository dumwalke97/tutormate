"""Subject and task pages grounded in the product, not in guessed search volume.

Algebra: the checker compares numbers (within 0.01) and explains the step.
Biology: the quiz box's own placeholder topic is "10th Grade Biology Photosynthesis",
and every generated question has exactly four choices.
Written answers: non-numeric answers are compared as text. The checker prompt
asks for the student's visible answer, the correct answer, and an explanation.
"""


def _faq_entities(pairs):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in pairs
        ],
    }


def _faq_html(pairs):
    blocks = []
    for question, answer in pairs:
        blocks.append(
            "            <div>\n"
            f"                <h3 class=\"font-semibold text-navy-900\">{question}</h3>\n"
            f"                <p class=\"mt-2 text-slate-600 leading-relaxed\">{answer}</p>\n"
            "            </div>"
        )
    return "\n".join(blocks)


def add_guide_pages(page, site):
    _algebra(page, site)
    _biology(page, site)
    _written(page, site)


def _algebra(page, site):
    faq = [
        (
            "Can TutorMate check algebra I already finished?",
            "Yes. Finish the problems, photograph the page or upload a picture of it, and TutorMate "
            "reads each answer. The check is written as the question, the answer it sees, the correct "
            "answer, and an explanation. The first 10 checks are free, then $4.95 per month or $49 per year.",
        ),
        (
            "Will it solve the equation before I try?",
            "The check button requires a page you upload. The intended use is a finished attempt. "
            "Photomath is the tool to open when you are stuck in the middle of a method. TutorMate is "
            "the tool to open after you have an answer written down.",
        ),
        (
            "How close does a numeric answer have to be?",
            "When the answer is a number, TutorMate treats it as a match if it is within 0.01 of the "
            "correct value. That covers ordinary rounding. A wrong method, such as forgetting to "
            "distribute, is not within 0.01, and the explanation should say which step failed.",
        ),
    ]
    page(
        "/algebra/",
        "Check Algebra Homework You Already Finished | TutorMate",
        "Photograph finished algebra and see which step failed. A worked example of 3(x - 2) = 15 shows a distribution error and the correct value, x = 7.",
        [
            {
                "@type": "WebPage",
                "@id": f"{site}/algebra/#page",
                "name": "Check algebra homework you already finished",
                "url": f"{site}/algebra/",
                "publisher": {"@id": f"{site}/#publisher"},
                "about": {"@id": f"{site}/#app"},
            },
            {
                "@type": "HowTo",
                "@id": f"{site}/algebra/#howto",
                "name": "How to check a finished algebra page",
                "totalTime": "PT2M",
                "step": [
                    {"@type": "HowToStep", "position": 1, "name": "Solve the problems yourself",
                     "text": "Write your own work, including the steps, on paper or in a document."},
                    {"@type": "HowToStep", "position": 2, "name": "Photograph the whole page",
                     "text": "Open TutorMate in the browser or in the iPhone app and photograph the page in good light, or upload an image, PDF, or document."},
                    {"@type": "HowToStep", "position": 3, "name": "Read each answer and the explanation",
                     "text": "TutorMate lists the answer it read, the correct answer, and the step that went wrong. Numbers within 0.01 count as a match."},
                    {"@type": "HowToStep", "position": 4, "name": "Practice the method you missed",
                     "text": "Generate a multiple-choice quiz on that algebra topic and save it in a folder."},
                ],
            },
            {
                "@type": "LearningResource",
                "@id": f"{site}/algebra/#example",
                "name": "Educational illustration: a distribution error in 3(x - 2) = 15",
                "learningResourceType": "worked example",
                "educationalUse": "illustration",
                "isAccessibleForFree": True,
                "description": "A textbook-style algebra example written for this page. It is not a TutorMate screenshot or a recorded product response.",
            },
            dict(_faq_entities(faq), **{"@id": f"{site}/algebra/#faq"}),
        ],
        f"""    <main class="max-w-3xl mx-auto px-6 py-14">
        <nav aria-label="Breadcrumb" class="text-xs text-slate-500">
            <a href="/" class="hover:text-navy-700 underline">TutorMate</a>
            <span class="mx-1">/</span>
            <span>Algebra</span>
        </nav>

        <h1 class="font-title text-3xl text-navy-900 mt-4">Check algebra homework you already finished</h1>

        <p class="mt-6 text-lg text-slate-700 leading-relaxed">
            TutorMate checks algebra you have already worked. Photograph the page and it reads each
            answer, states the correct value, and explains the step that failed. Open it after you have
            an answer on the page, not instead of trying. Your first 10 checks are free.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">A distribution error, worked by hand</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            This is the kind of finished work the checker is for. The arithmetic below is a textbook
            example written for this page. It is not a screenshot and not a recorded TutorMate response.
            The recording of the actual product is the
            <a href="/#how-it-works" class="text-navy-700 underline">demo on the homepage</a>.
        </p>

        <figure class="mt-6 rounded-xl border border-slate-200 bg-white p-5">
            <figcaption class="text-xs font-semibold uppercase tracking-wide text-slate-500">Educational illustration</figcaption>
            <p class="mt-4 font-semibold text-slate-900">Solve 3(x - 2) = 15.</p>
            <p class="mt-3 text-sm font-semibold text-slate-900">A finished attempt that drops the distribution</p>
            <ol class="mt-2 list-decimal list-inside text-slate-700 leading-relaxed">
                <li>3(x - 2) = 15</li>
                <li>3x - 2 = 15</li>
                <li>3x = 17</li>
                <li>x = 17/3</li>
            </ol>
            <p class="mt-3 text-slate-600 leading-relaxed">
                Line 2 is the mistake. Multiplying only the x by 3 leaves the 2 untouched, so the rest
                of the arithmetic is solving a different equation. Checking that result fails:
                3(17/3 - 2) = 3(17/3 - 6/3) = 3(11/3) = 11, which is not 15.
            </p>
            <p class="mt-4 text-sm font-semibold text-slate-900">The correct steps</p>
            <ol class="mt-2 list-decimal list-inside text-slate-700 leading-relaxed">
                <li>3(x - 2) = 15</li>
                <li>3x - 6 = 15, because 3 times -2 is -6</li>
                <li>3x = 21</li>
                <li>x = 7</li>
            </ol>
            <p class="mt-3 text-slate-600 leading-relaxed">
                Check: 3(7 - 2) = 3(5) = 15. The correct value is x = 7.
            </p>
        </figure>

        <h2 class="font-title text-2xl text-navy-900 mt-12">What you actually get back</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            For each question on the page, the check is organized as the problem, the answer it could
            read, the correct answer, and a short explanation of how to get there. On a page like the
            one above, the useful part is not only "x = 7". It is seeing that the 3 never reached the
            second term. Numeric answers within 0.01 of the correct value count as a match, so ordinary
            rounding is not marked wrong. A result such as 17/3 is not within 0.01 of 7.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Handwritten algebra is supported. A clear photo of the whole page is more reliable than a
            crop of one line or a shot with a heavy shadow. You can also upload an image, a PDF, or a
            Word document. The same page can be saved in a folder and opened later on the web or on the
            iPhone app.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">How to check a finished algebra page</h2>
        <ol class="mt-4 space-y-4 text-slate-600 leading-relaxed list-decimal list-inside">
            <li><strong class="text-slate-900">Do the problems first.</strong> Leave the steps on the page. The explanation is about the method you used.</li>
            <li><strong class="text-slate-900">Photograph the page.</strong> Use the browser or the iPhone app. Include the whole problem, not only the final line.</li>
            <li><strong class="text-slate-900">Read the explanation, not only the mark.</strong> Compare the correct value with the line where your method changed.</li>
            <li><strong class="text-slate-900">Practice that method.</strong> Generate a multiple-choice quiz on the topic and save it. Quizzes have four choices per question. On a new quiz you can ask for 5, 10, 15, 20, 25, or 30 questions.</li>
        </ol>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Checker, not a computer-algebra app</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            TutorMate does not graph equations, and it is not a dedicated algebra solver. If you are
            stuck before you have an answer,
            <a href="/vs/photomath/" class="text-navy-700 underline">Photomath does that job</a> and
            TutorMate does not replace it. If the page is already filled in, including word problems
            and other subjects mixed onto the same sheet, the check covers the page rather than one
            expression at a time. For answers that are sentences instead of numbers, use the
            <a href="/written-answers/" class="text-navy-700 underline">written-answer check</a>.
            To drill the topic afterward, start from the
            <a href="/quiz-generator/" class="text-navy-700 underline">quiz generator</a> or the
            <a href="/biology/" class="text-navy-700 underline">biology quiz example</a>.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Common questions</h2>
        <div class="mt-6 space-y-8">
{_faq_html(faq)}
        </div>
    </main>
""",
        [("TutorMate", "/"), ("Algebra", "/algebra/")],
    )


def _biology(page, site):
    faq = [
        (
            "Can TutorMate quiz me on photosynthesis from my notes?",
            "Yes. Type a topic such as 10th grade photosynthesis, paste your notes, or photograph a "
            "worksheet or textbook page. TutorMate builds a multiple-choice quiz from that material. "
            "The first 10 quizzes are free, then $4.95 per month or $49 per year.",
        ),
        (
            "How many questions, and what do they look like?",
            "Each question has exactly four choices, and one of those choices is the answer. On a new "
            "quiz you pick 5, 10, 15, 20, 25, or 30 questions. A quiz made from files already saved in "
            "a folder can be longer, up to 100 questions. The questions are phrased from the facts in "
            "your material, not as 'according to the image'.",
        ),
        (
            "Is the sample question on this page a real TutorMate result?",
            "No. The question about the thylakoid membrane was written for this page as an educational "
            "illustration. It is not a screenshot, a testimonial, or a saved TutorMate quiz. The "
            "homepage demo video is the genuine product recording.",
        ),
    ]
    page(
        "/biology/",
        "Photosynthesis Practice Quiz from Your Notes | TutorMate",
        "Build a four-choice biology quiz from notes or a topic such as photosynthesis. Includes a textbook-style illustration, not a captured TutorMate result.",
        [
            {
                "@type": "WebPage",
                "@id": f"{site}/biology/#page",
                "name": "Photosynthesis practice quiz from your notes",
                "url": f"{site}/biology/",
                "publisher": {"@id": f"{site}/#publisher"},
                "about": {"@id": f"{site}/#app"},
            },
            {
                "@type": "HowTo",
                "@id": f"{site}/biology/#howto",
                "name": "How to make a biology practice quiz",
                "totalTime": "PT1M",
                "step": [
                    {"@type": "HowToStep", "position": 1, "name": "Give TutorMate the material",
                     "text": "Type a topic, paste class notes, photograph a worksheet, or upload a PDF or document."},
                    {"@type": "HowToStep", "position": 2, "name": "Choose how many questions",
                     "text": "Pick 5, 10, 15, 20, 25, or 30 questions. Each question has four choices."},
                    {"@type": "HowToStep", "position": 3, "name": "Answer and read the misses",
                     "text": "Take the quiz. Missed questions are the ones to review in your notes."},
                    {"@type": "HowToStep", "position": 4, "name": "Save the quiz in a folder",
                     "text": "Folders sync between the website and the iPhone app, so you can retake the quiz later."},
                ],
            },
            {
                "@type": "LearningResource",
                "@id": f"{site}/biology/#example",
                "name": "Educational illustration: photosynthesis organelle and a four-choice question",
                "learningResourceType": "worked example",
                "educationalUse": "illustration",
                "isAccessibleForFree": True,
                "description": "A textbook-style biology example and a four-choice question written for this page. Not a TutorMate screenshot or recorded quiz.",
            },
            dict(_faq_entities(faq), **{"@id": f"{site}/biology/#faq"}),
        ],
        f"""    <main class="max-w-3xl mx-auto px-6 py-14">
        <nav aria-label="Breadcrumb" class="text-xs text-slate-500">
            <a href="/" class="hover:text-navy-700 underline">TutorMate</a>
            <span class="mx-1">/</span>
            <span>Biology</span>
        </nav>

        <h1 class="font-title text-3xl text-navy-900 mt-4">A photosynthesis quiz from your own notes</h1>

        <p class="mt-6 text-lg text-slate-700 leading-relaxed">
            TutorMate builds a multiple-choice biology quiz from a topic you type, notes you paste, or
            a page you photograph. The quiz box on the app uses "10th Grade Biology Photosynthesis" as
            one of its two example topics. Your first 10 quizzes are free.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Why the quiz is built from your material</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            A general biology bank will ask about every unit. Your test usually will not. If this week
            is photosynthesis, a quiz made from your worksheet or from that topic stays on chlorophyll,
            the chloroplast, and the two stages of the reactions. Re-reading the notes makes the page
            look familiar. Answering a question forces you to retrieve the fact, which is the practice
            that transfers to a test. The
            <a href="/quiz-generator/" class="text-navy-700 underline">quiz generator</a> is the full
            description of the four ways to start.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">The facts, then one practice question</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            The notes and the question below were written for this page. They are an educational
            illustration of the material and of the four-choice shape TutorMate uses. They are not a
            screenshot, a testimonial, or a quiz the product produced. The genuine product recording
            is the <a href="/#how-it-works" class="text-navy-700 underline">homepage demo</a>.
        </p>

        <figure class="mt-6 rounded-xl border border-slate-200 bg-white p-5">
            <figcaption class="text-xs font-semibold uppercase tracking-wide text-slate-500">Educational illustration</figcaption>
            <p class="mt-4 font-semibold text-slate-900">A short photosynthesis note</p>
            <p class="mt-3 text-slate-700 leading-relaxed">
                In plants, photosynthesis takes place in the chloroplast. Chlorophyll is the main
                pigment. It absorbs mostly blue and red light and reflects green light, which is why
                leaves look green. The light-dependent reactions happen in the thylakoid membrane.
                Those reactions use light to split water and release oxygen. The Calvin cycle happens
                in the stroma. It uses carbon dioxide, ATP, and NADPH to build sugar. A common summary
                of the whole process is 6CO2 + 6H2O, with light, gives C6H12O6 + 6O2.
            </p>
            <p class="mt-4 text-sm font-semibold text-slate-900">A finished short answer, and what is wrong with it</p>
            <p class="mt-2 text-slate-700 leading-relaxed">
                Question: name the organelle where photosynthesis occurs, and the pigment that absorbs
                the light. Student answer: "It happens in the mitochondria. The pigment is chlorophyll."
                The pigment is right. The organelle is not. Mitochondria run cellular respiration.
                Photosynthesis runs in the chloroplast.
            </p>
            <p class="mt-4 text-sm font-semibold text-slate-900">One four-choice question in the same shape as a TutorMate quiz</p>
            <p class="mt-2 text-slate-700 leading-relaxed">Where do the light-dependent reactions of photosynthesis take place?</p>
            <ul class="mt-2 list-disc list-inside text-slate-700 leading-relaxed">
                <li>In the stroma</li>
                <li>In the thylakoid membrane</li>
                <li>In the nucleus</li>
                <li>In the mitochondrion</li>
            </ul>
            <p class="mt-3 text-slate-700 leading-relaxed">
                Answer: in the thylakoid membrane. The stroma is where the Calvin cycle runs. The
                nucleus holds the cell's DNA. The mitochondrion is the respiration organelle.
            </p>
        </figure>

        <h2 class="font-title text-2xl text-navy-900 mt-12">What the quiz button actually makes</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Questions are multiple choice, with exactly four options, and the marked answer is one of
            those four strings. On a new quiz you choose 5, 10, 15, 20, 25, or 30 questions. If you
            are quizzing files you already saved in a folder, the count can go up to 100. You can start
            from a typed topic, pasted notes, a photo, a PDF, or a Word document. There is no separate
            biology mode and no promise that every generated question will be the one above. The model
            writes new questions from the material you give it, so a different set of notes produces a
            different quiz.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            You can also photograph a finished biology worksheet and check the short answers, the same
            way you would check any other completed page. That path is described on
            <a href="/homework-help/" class="text-navy-700 underline">homework help</a> and
            <a href="/written-answers/" class="text-navy-700 underline">written answers</a>. Numeric
            work, if the sheet has calculations, is covered with the
            <a href="/algebra/" class="text-navy-700 underline">algebra check</a>.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">How to make the quiz</h2>
        <ol class="mt-4 space-y-4 text-slate-600 leading-relaxed list-decimal list-inside">
            <li><strong class="text-slate-900">Use the material you will be tested on.</strong> A typed topic works when you have nothing else. Your own notes are closer to the test.</li>
            <li><strong class="text-slate-900">Pick a count you will finish.</strong> Ten questions is the default on a new quiz. Four choices each.</li>
            <li><strong class="text-slate-900">Miss a question, then find it in the notes.</strong> The point is to see the gap while the worksheet is still around.</li>
            <li><strong class="text-slate-900">Save it.</strong> Folders sync between the browser and the iPhone app, so the retake does not have to happen at the same desk.</li>
        </ol>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Common questions</h2>
        <div class="mt-6 space-y-8">
{_faq_html(faq)}
        </div>
    </main>
""",
        [("TutorMate", "/"), ("Biology", "/biology/")],
    )


def _written(page, site):
    faq = [
        (
            "Can TutorMate check answers that are not math?",
            "Yes. The checker reads the page and writes down the answer it sees, the correct answer, "
            "and an explanation. That includes definitions, vocabulary, and short history or science "
            "answers. The first 10 checks are free, then $4.95 per month or $49 per year.",
        ),
        (
            "What if my sentence is right but worded differently?",
            "A written answer is highlighted as a match when the text lines up with the correct answer, "
            "ignoring capitalization and extra spaces. A correct idea in different words may not get "
            "that highlight. Read the explanation, which is where the reasoning is written out. Numbers "
            "are different: they count as a match within 0.01.",
        ),
        (
            "Can it check a page that mixes sentences and calculations?",
            "Yes. One uploaded page can contain both. Numeric items use the number comparison. "
            "Sentences use the text comparison. You do not pick a subject mode before you upload.",
        ),
    ]
    page(
        "/written-answers/",
        "Check Short Written Answers, Not Just Math | TutorMate",
        "Check definitions and short written answers on a finished page. A primary-source example shows what a text match means, and where different wording still needs the explanation.",
        [
            {
                "@type": "WebPage",
                "@id": f"{site}/written-answers/#page",
                "name": "Check short written answers, not just math",
                "url": f"{site}/written-answers/",
                "publisher": {"@id": f"{site}/#publisher"},
                "about": {"@id": f"{site}/#app"},
            },
            {
                "@type": "HowTo",
                "@id": f"{site}/written-answers/#howto",
                "name": "How to check short written answers",
                "totalTime": "PT2M",
                "step": [
                    {"@type": "HowToStep", "position": 1, "name": "Write the answers yourself",
                     "text": "Complete the definitions or short answers in your own words."},
                    {"@type": "HowToStep", "position": 2, "name": "Photograph the finished page",
                     "text": "Use the browser or the iPhone app. A clear photo of the whole page works better than a tight crop."},
                    {"@type": "HowToStep", "position": 3, "name": "Compare your wording with the explanation",
                     "text": "The check shows the answer it read, a correct answer, and an explanation. Identical wording is highlighted as a match. A right idea in different words may not be, so read the explanation."},
                    {"@type": "HowToStep", "position": 4, "name": "Turn the misses into a quiz",
                     "text": "Generate a four-choice quiz from the same page or from the topic and save it in a folder."},
                ],
            },
            {
                "@type": "LearningResource",
                "@id": f"{site}/written-answers/#example",
                "name": "Educational illustration: primary source versus textbook",
                "learningResourceType": "worked example",
                "educationalUse": "illustration",
                "isAccessibleForFree": True,
                "description": "A textbook-style definition example written for this page. It is not a TutorMate screenshot or a recorded product response.",
            },
            dict(_faq_entities(faq), **{"@id": f"{site}/written-answers/#faq"}),
        ],
        f"""    <main class="max-w-3xl mx-auto px-6 py-14">
        <nav aria-label="Breadcrumb" class="text-xs text-slate-500">
            <a href="/" class="hover:text-navy-700 underline">TutorMate</a>
            <span class="mx-1">/</span>
            <span>Written answers</span>
        </nav>

        <h1 class="font-title text-3xl text-navy-900 mt-4">Check short written answers, not just math</h1>

        <p class="mt-6 text-lg text-slate-700 leading-relaxed">
            TutorMate checks a finished page of definitions, vocabulary, or short answers. It reads
            what you wrote, states a correct answer, and explains the difference. A math solver cannot
            do that job, because there is no equation to solve. Your first 10 checks are free.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">A definition, worked as a check</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            The answer below was written for this page as an educational illustration. It is not a
            screenshot and not something TutorMate returned. The
            <a href="/#how-it-works" class="text-navy-700 underline">homepage demo</a> is the real
            product recording.
        </p>

        <figure class="mt-6 rounded-xl border border-slate-200 bg-white p-5">
            <figcaption class="text-xs font-semibold uppercase tracking-wide text-slate-500">Educational illustration</figcaption>
            <p class="mt-4 font-semibold text-slate-900">Question. Define a primary source and give one example.</p>
            <p class="mt-3 text-slate-700 leading-relaxed">
                Student answer: "A primary source is a textbook written about an event. An example is
                a history textbook."
            </p>
            <p class="mt-3 text-slate-700 leading-relaxed">
                That swaps the two categories. A primary source is a firsthand account or an artifact
                from the time being studied: a diary, a letter, a photograph, a speech, or an official
                record created then. A textbook written later, by someone who was not there, is a
                secondary source. It discusses the event. It is not the event's own record.
            </p>
            <p class="mt-3 text-slate-700 leading-relaxed">
                A corrected answer: "A primary source is a firsthand account or artifact from the time
                being studied. A diary kept during the event is a primary source. A textbook written
                later is a secondary source."
            </p>
        </figure>

        <h2 class="font-title text-2xl text-navy-900 mt-12">How a written answer is judged</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            After the explanation is written, the page highlights the student's answer as a match when
            the text lines up with the correct answer. Capitalization and extra spaces are ignored. A
            sentence that is right in substance but worded differently can fail that highlight. The
            explanation is the part to read in that case. It is not a rubric score from your teacher,
            and it is not a claim that the wording match is a grade.
        </p>
        <p class="mt-4 text-slate-600 leading-relaxed">
            Numbers on the same page are handled separately. Two numbers within 0.01 count as a match,
            which is the rule described on the
            <a href="/algebra/" class="text-navy-700 underline">algebra</a> page. Parts labeled like
            "a)" and "b)", or "1." and "2.", are compared one part at a time when both the student's
            answer and the correct answer use those labels. You do not choose a subject first. History,
            vocabulary, and science short answers go through the same check as a math page. More of
            the workflow is on <a href="/homework-help/" class="text-navy-700 underline">homework help</a>.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">How to check the page</h2>
        <ol class="mt-4 space-y-4 text-slate-600 leading-relaxed list-decimal list-inside">
            <li><strong class="text-slate-900">Answer in your own handwriting or typing.</strong> The check needs a completed attempt on the page.</li>
            <li><strong class="text-slate-900">Photograph the whole answer.</strong> A cropped line is easier to misread. Handwriting is supported when the photo is clear and lit.</li>
            <li><strong class="text-slate-900">Read the explanation beside the highlight.</strong> A green highlight means the text matched. It does not mean every possible correct wording would match.</li>
            <li><strong class="text-slate-900">Practice the terms you missed.</strong> The <a href="/quiz-generator/" class="text-navy-700 underline">quiz generator</a> can turn the same notes into four-choice questions. A biology example of that shape is on the <a href="/biology/" class="text-navy-700 underline">photosynthesis page</a>.</li>
        </ol>

        <h2 class="font-title text-2xl text-navy-900 mt-12">What this is not</h2>
        <p class="mt-4 text-slate-600 leading-relaxed">
            It is not an essay grader, and it does not return a rubric score for a multi-paragraph
            paper. It is built for the question-by-question page: a definition, a vocabulary item, a
            short answer. It also does not replace a solver when you have not started a math problem.
            That difference is spelled out in
            <a href="/vs/photomath/" class="text-navy-700 underline">TutorMate versus Photomath</a>.
        </p>

        <h2 class="font-title text-2xl text-navy-900 mt-12">Common questions</h2>
        <div class="mt-6 space-y-8">
{_faq_html(faq)}
        </div>
    </main>
""",
        [("TutorMate", "/"), ("Written answers", "/written-answers/")],
    )
