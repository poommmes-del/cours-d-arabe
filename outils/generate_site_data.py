#!/usr/bin/env python3
"""Generer le catalogue JSON de l'interface des cours."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = ROOT / "archive-items"
AUDIO_MANIFEST = ROOT / "audios-opus" / "manifest.tsv"
SOURCES_MD = ROOT / "livres" / "sources.md"
PEDAGOGICAL_DIR = ROOT / "cours-pedagogiques"
SITE_DATA = ROOT / "site" / "data"


COURSE_GROUPS = {
    "ajroumiya": ("Nahw", 1),
    "moutammima": ("Nahw", 2),
    "qatr-nada": ("Nahw", 3),
    "qawaid-i3raab-sa3di": ("Nahw", 4),
    "qawaid-i3raab-zawawi": ("Nahw", 5),
    "mawsil-toullab": ("Nahw", 6),
    "shoudhour-dhahab": ("Nahw", 7),
    "alfiya-nahw": ("Nahw", 8),
    "moulakhas-sarfi": ("Sarf", 9),
    "nadhm-maqsoud": ("Sarf", 10),
    "alfiya-sarf": ("Sarf", 11),
    "laamiya-af3al": ("Sarf", 12),
    "dourous-balagha": ("Balagha", 13),
    "maani-we-bayan": ("Balagha", 14),
}
GROUP_ORDER = {"Nahw": 1, "Sarf": 2, "Balagha": 3, "Autre": 99}


@dataclass(frozen=True)
class AudioRow:
    name: str
    length_seconds: float
    source_size_bytes: int
    url: str


def rel(path: Path) -> str:
    return "../" + path.relative_to(ROOT).as_posix()


def natural_key(value: str) -> list[int | str]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def seconds_to_label(seconds: float) -> str:
    total = int(round(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^\w\u0600-\u06ff]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "module"


def markdown_excerpt(markdown: str, limit: int = 180) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", markdown)
    text = re.sub(r"[*_#|>-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[: limit - 1] + "…" if len(text) > limit else text


QUIZ_TERMS = [
    "الكلام",
    "الكلمة",
    "الإعراب",
    "البناء",
    "العامل",
    "الرفع",
    "النصب",
    "الخفض",
    "الجر",
    "الجزم",
    "الاسم",
    "الفعل",
    "الحرف",
    "الفاعل",
    "نائب الفاعل",
    "المبتدأ",
    "الخبر",
    "كان وأخواتها",
    "إن وأخواتها",
    "ظن وأخواتها",
    "المفعول به",
    "الحال",
    "التمييز",
    "المجرورات",
    "التوابع",
    "النعت",
    "العطف",
    "التوكيد",
    "البدل",
    "الميزان",
    "الوزن",
    "المصدر",
    "الإعلال",
    "الإبدال",
    "التشبيه",
    "الاستعارة",
    "الكناية",
    "المجاز",
]


def strip_markdown(markdown: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", markdown)
    text = re.sub(r"[*_#|>-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_quiz_terms(title: str, markdown: str) -> list[str]:
    text = f"{title} {strip_markdown(markdown)}"
    found = [term for term in QUIZ_TERMS if term in text]
    if found:
        return found[:4]
    words = re.findall(r"[\u0600-\u06ff]{4,}", text)
    seen: list[str] = []
    for word in words:
        if word not in seen:
            seen.append(word)
        if len(seen) >= 4:
            break
    return seen or ["المسألة"]


def extract_quiz_examples(markdown: str) -> list[str]:
    examples = []
    for value in re.findall(r"`([^`]+)`", markdown):
        clean = re.sub(r"\s+", " ", value).strip()
        if 2 <= len(clean) <= 70 and any("\u0600" <= char <= "\u06ff" for char in clean):
            examples.append(clean)
    unique: list[str] = []
    for example in examples:
        if example not in unique:
            unique.append(example)
        if len(unique) >= 4:
            break
    return unique


def specialized_questions(title: str, markdown: str) -> list[dict[str, str]]:
    if title == "Accueil" and "الآجرومية" in markdown:
        return qa(
            ("ما الهدف العملي من دراسة الآجرومية؟", "أن يعرف الطالب وظيفة الكلمة وحالتها الإعرابية وعلامتها، ثم يعرب الجمل السهلة."),
            ("لماذا يبدأ الطالب بوظيفة الكلمة قبل العلامة؟", "لأن العلامة لا تفهم وحدها؛ لا بد أولًا من معرفة هل الكلمة فاعل أو مفعول أو مبتدأ أو غير ذلك."),
            ("ما أقسام الكلمة التي يبنى عليها أول الدرس؟", "أقسام الكلمة ثلاثة: اسم، وفعل، وحرف."),
            ("في `قام زيدٌ`: أعرب إجمالًا.", "`قام`: فعل ماض، و`زيدٌ`: فاعل مرفوع."),
            ("اذكر مثالًا لجملة مفيدة تصلح للتدريب الأول.", "مثل: `جاء الطالبُ`؛ لأنها مركبة ومفيدة، وفيها فعل وفاعل."),
        )

    banks: list[tuple[str, list[tuple[str, str]]]] = [
        (
            "طريقة الدراسة",
            [
                ("ما خطوات الدراسة المختصرة لهذا المقرر؟", "اقرأ للفهم، احفظ التعريف المختصر، طبّق على الأمثلة، ثم انتقل إلى الاختبار."),
                ("لماذا لا تبدأ بحفظ الإعراب مباشرة؟", "لأن الإعراب نتيجة؛ فلا بد قبلها من معرفة نوع الكلمة ووظيفتها في الجملة."),
                ("أكمل: اقرأ الدرس مرة للفهم، ثم ...", "احفظ التعريف المختصر، ثم طبّق على الأمثلة، ثم اختبر نفسك."),
                ("في `قام زيدٌ`: ما الذي تبحث عنه قبل علامة الرفع؟", "أبحث أولًا عن وظيفة `زيدٌ`: هو فاعل، ثم أذكر أنه مرفوع."),
                ("اذكر مثالًا لطريقة مذاكرة صحيحة بعد سماع الدرس.", "أكتب مثالًا جديدًا، أحدد نوع كل كلمة، ثم أعربه وأقارن الجواب بالشرح."),
            ],
        ),
        (
            "الكلام وأقسام الكلمة",
            [
                ("عرّف الكلام عند النحاة.", "الكلام هو اللفظ المركب المفيد بالوضع."),
                ("ما معنى قولهم: مفيد؟", "أي يحسن سكوت المتكلم عليه، فلا ينتظر السامع تمامًا ضروريًا."),
                ("اذكر ثلاث علامات للاسم.", "`ال`، والتنوين، والجر، والإسناد إليه."),
                ("صنّف: `كتاب`, `كتب`, `من`.", "`كتاب`: اسم، و`كتب`: فعل، و`من`: حرف."),
                ("في `قام زيدٌ`: استخرج الاسم والفعل.", "`قام`: فعل، و`زيدٌ`: اسم."),
            ],
        ),
        (
            "الإعراب والبناء",
            [
                ("عرّف الإعراب.", "الإعراب تغير أواخر الكلم لاختلاف العوامل الداخلة عليها لفظًا أو تقديرًا."),
                ("ما معنى العامل في باب الإعراب؟", "العامل هو السبب الذي يطلب حالة إعرابية في الكلمة."),
                ("اذكر الأحوال الإعرابية الأربعة.", "الرفع، والنصب، والخفض أو الجر، والجزم."),
                ("ما الفرق بين المعرب والمبني؟", "المعرب يتغير آخره بحسب العامل، والمبني يلزم آخره حالة واحدة."),
                ("في `لم يذهبْ`: استخرج العامل والحكم.", "`لم` عامل جزم، و`يذهبْ` فعل مضارع مجزوم بالسكون."),
            ],
        ),
        (
            "علامات الإعراب",
            [
                ("ما علامة الرفع الأصلية؟", "علامة الرفع الأصلية هي الضمة."),
                ("ما علامة نصب جمع المؤنث السالم؟", "ينصب جمع المؤنث السالم بالكسرة نيابة عن الفتحة."),
                ("في `جَاءَ الطَّالِبَانِ`: أعرب `الطَّالِبَانِ`.", "`الطَّالِبَانِ`: فاعل مرفوع بالألف لأنه مثنى."),
                ("في `مَرَرْتُ بِأَحْمَدَ`: لماذا جُرَّ بالفتحة؟", "لأنه ممنوع من الصرف، ولم تدخل عليه `ال` ولم يضف."),
                ("ما الفرق بين `لَنْ يَكْتُبُوا` و`لَمْ يَكْتُبُوا`؟", "`لَنْ` تنصب، و`لَمْ` تجزم، والعلامة في الفعلين حذف النون."),
            ],
        ),
        (
            "الأسماء الملحقة والعلامات الفرعية",
            [
                ("ما علامة رفع المثنى؟", "يرفع المثنى بالألف."),
                ("ما علامة نصب وجر جمع المذكر السالم؟", "ينصب ويجر بالياء."),
                ("اذكر شروط إعراب الأسماء الخمسة بالحروف.", "أن تكون مفردة، مكبرة، مضافة، ومضافة إلى غير ياء المتكلم."),
                ("في `رأيت أباكَ`: أعرب `أباكَ`.", "`أباكَ`: مفعول به منصوب بالألف لأنه من الأسماء الخمسة."),
                ("في `مررت بالطالبين`: استخرج العلامة وسببها.", "العلامة الياء؛ لأن `الطالبين` مثنى مجرور."),
            ],
        ),
        (
            "الأفعال",
            [
                ("ما أنواع الفعل؟", "الفعل ثلاثة: ماض، ومضارع، وأمر."),
                ("متى يرفع المضارع؟", "يرفع إذا لم يسبقه ناصب ولا جازم."),
                ("اذكر أربع أدوات تجزم فعلًا واحدًا.", "`لم`، و`لما`، ولام الأمر، ولا الناهية."),
                ("أعرب `لم يذهبْ زيدٌ`.", "`لم`: حرف جزم، و`يذهبْ`: مضارع مجزوم بالسكون، و`زيدٌ`: فاعل مرفوع."),
                ("أكمل جواب الشرط: `إن تدرسْ ...`.", "تقول: `إن تدرسْ تنجحْ`، فيجزم فعل الشرط وجوابه."),
            ],
        ),
        (
            "المرفوعات",
            [
                ("اذكر أهم المرفوعات في هذا المستوى.", "الفاعل، ونائب الفاعل، والمبتدأ، والخبر، واسم كان، وخبر إن، والتابع للمرفوع."),
                ("عرّف الفاعل.", "الفاعل اسم مرفوع وقع بعد فعل مبني للمعلوم ودل على من فعل الفعل أو قام به."),
                ("ما نائب الفاعل؟", "اسم مرفوع يأتي بعد فعل مبني للمجهول."),
                ("في `كتب الطالبُ الدرسَ`: أعرب `الطالبُ`.", "`الطالبُ`: فاعل مرفوع بالضمة."),
                ("في `زيدٌ قائمٌ`: استخرج المبتدأ والخبر.", "`زيدٌ`: مبتدأ، و`قائمٌ`: خبر، وكلاهما مرفوع."),
            ],
        ),
        (
            "النواسخ",
            [
                ("ماذا تعمل `كان وأخواتها`؟", "ترفع الاسم وتنصب الخبر."),
                ("ماذا تعمل `إن وأخواتها`؟", "تنصب الاسم وترفع الخبر."),
                ("ماذا تعمل `ظن وأخواتها`؟", "تنصب مفعولين أصلهما المبتدأ والخبر."),
                ("أعرب إجمالًا `كان زيدٌ قائمًا`.", "`كان`: ناسخ، و`زيدٌ`: اسم كان مرفوع، و`قائمًا`: خبر كان منصوب."),
                ("في `إن زيدًا قائمٌ`: استخرج اسم إن وخبرها.", "`زيدًا`: اسم إن منصوب، و`قائمٌ`: خبر إن مرفوع."),
            ],
        ),
        (
            "المنصوبات",
            [
                ("اذكر خمسة من المنصوبات.", "المفعول به، والمفعول المطلق، والظرف، والحال، والتمييز، والمنادى، واسم إن."),
                ("عرّف المفعول به.", "اسم منصوب وقع عليه فعل الفاعل."),
                ("ما المفعول المطلق؟", "مصدر منصوب من لفظ الفعل أو معناه."),
                ("في `قرأ الطالبُ الدرسَ`: أعرب `الدرسَ`.", "`الدرسَ`: مفعول به منصوب بالفتحة."),
                ("في `جاء زيدٌ راكبًا`: ما وظيفة `راكبًا`؟", "`راكبًا`: حال منصوب يبين هيئة صاحبه."),
            ],
        ),
        (
            "المنادى ولا النافية للجنس والاستثناء",
            [
                ("ما المنادى؟", "اسم يطلب إقباله بحرف نداء ملفوظ أو مقدر."),
                ("ما عمل `لا` النافية للجنس؟", "تنصب الاسم وترفع الخبر إذا استوفت شروطها."),
                ("في `يا زيدُ`: أعرب `زيدُ`.", "منادى علم مفرد مبني على الضم في محل نصب."),
                ("في `لا رجلَ في الدار`: استخرج اسم لا.", "`رجلَ`: اسم لا النافية للجنس منصوب."),
                ("ما أركان الاستثناء؟", "المستثنى منه، وأداة الاستثناء، والمستثنى."),
            ],
        ),
        (
            "المجرورات",
            [
                ("اذكر أنواع المجرورات.", "مجرور بحرف جر، ومجرور بالإضافة، وتابع للمجرور."),
                ("اذكر خمسة من حروف الجر.", "`من`، `إلى`، `عن`، `على`، `في`، والباء، واللام، والكاف."),
                ("في `جلست في البيتِ`: أعرب `البيتِ`.", "`البيتِ`: اسم مجرور بـ`في` وعلامة جره الكسرة."),
                ("في `كتابُ الطالبِ`: لماذا جُرَّ `الطالبِ`؟", "لأنه مضاف إليه مجرور."),
                ("استخرج الجار والمجرور من `سافرت من المدينةِ`.", "الجار `من`، والمجرور `المدينةِ`."),
            ],
        ),
        (
            "التوابع",
            [
                ("ما التوابع؟", "كلمات تتبع ما قبلها في الإعراب."),
                ("اذكر أنواع التوابع.", "النعت، والعطف، والتوكيد، والبدل."),
                ("في `جاء الطالبُ المجتهدُ`: استخرج النعت والمنعوت.", "المنعوت `الطالبُ`، والنعت `المجتهدُ` وهو تابع له."),
                ("ما الفرق بين العطف والنعت؟", "العطف بينه وبين متبوعه حرف عطف، أما النعت فيصف المنعوت."),
                ("في `قرأت الكتابَ مقدمتَه`: ما نوع البدل؟", "`مقدمتَه`: بدل بعض من كل."),
            ],
        ),
        (
            "طريقة الإعراب",
            [
                ("ما أول سؤال تسأله عند الإعراب؟", "هل الكلمة اسم أو فعل أو حرف؟"),
                ("ما الخطوات الخمس لإعراب الاسم؟", "نوع الكلمة، وظيفتها، حالتها الإعرابية، علامتها، وسبب الحكم."),
                ("أعرب `لم يقرأْ الولدُ الكتابَ في البيتِ` إجمالًا.", "`لم`: جازم، `يقرأْ`: مضارع مجزوم، `الولدُ`: فاعل، `الكتابَ`: مفعول به، `في البيتِ`: جار ومجرور."),
                ("في الجملة السابقة: استخرج حرف الجر والاسم المجرور.", "حرف الجر `في`، والاسم المجرور `البيتِ`."),
                ("لماذا لا تبدأ بعلامة آخر الكلمة؟", "لأن العلامة نتيجة للوظيفة والعامل، فلا بد من معرفة السبب أولًا."),
            ],
        ),
        (
            "خطة ثلاثين يومًا",
            [
                ("ما وظيفة الاختبارات في الخطة؟", "تثبيت ما سبق قبل الانتقال إلى مجموعة جديدة من الأبواب."),
                ("أين تظهر مراجعة المنصوبات في الخطة؟", "بعد دراسة أبواب المنصوبات، ثم يأتي اختبار بعدها."),
                ("أكمل خطة اليوم الأول: `الكلام و...`", "`الكلام وأقسام الكلمة`."),
                ("اذكر مثالًا لما تفعله في يوم المراجعة.", "أعيد قراءة التعاريف، أحل أمثلة، ثم أصحح الأخطاء من الشرح."),
                ("لماذا جعلت الخطة امتحانًا تجريبيًا قبل النهائي؟", "ليظهر النقص قبل الاختبار الأخير فيمكن تداركه."),
            ],
        ),
        (
            "بطاقة حفظ",
            [
                ("ما العلامات التي يعرف بها الاسم في البطاقة؟", "يقبل `ال` والتنوين والجر."),
                ("ما الأصل في علامات الرفع والنصب والجر والجزم؟", "الرفع بالضمة، والنصب بالفتحة، والجر بالكسرة، والجزم بالسكون."),
                ("اذكر ثلاثًا من المرفوعات المذكورة.", "الفاعل، ونائب الفاعل، والمبتدأ، والخبر."),
                ("اذكر مثالًا على مجرور بحرف جر.", "مثل: `مررت بزيدٍ`، فـ`زيدٍ` اسم مجرور بالباء."),
                ("كيف تستخدم بطاقة الحفظ بعد الدرس؟", "تراجع القواعد السريعة، ثم تختبرها على مثال جديد من إنشائك."),
            ],
        ),
    ]

    for marker, questions in banks:
        if marker in title:
            return qa(*questions)
    return []


def qa(*items: tuple[str, str]) -> list[dict[str, str]]:
    return [{"question": question, "answer": answer} for question, answer in items]


def default_questions(title: str, markdown: str) -> list[dict[str, str]]:
    specialized = specialized_questions(title, markdown)
    if specialized:
        return specialized

    terms = extract_quiz_terms(title, markdown)
    examples = extract_quiz_examples(markdown)
    first = terms[0]
    second = terms[1] if len(terms) > 1 else "مثاله"
    third = terms[2] if len(terms) > 2 else "سبب الحكم"
    example = examples[0] if examples else "جاء زيدٌ"
    second_example = examples[1] if len(examples) > 1 else example
    return [
        {
            "question": f"عرّف `{first}` بعبارة قصيرة.",
            "answer": f"`{first}` هو الباب المركزي في هذا الموضع، والمطلوب أن تعرف حده قبل تطبيق الأمثلة.",
        },
        {
            "question": f"ما الفرق العملي بين `{first}` و`{second}`؟",
            "answer": f"ابدأ بتعريف `{first}`، ثم بيّن علاقته بـ`{second}` من جهة الحكم أو الوظيفة في الجملة.",
        },
        {
            "question": f"في `{example}`: استخرج موضع `{first}` أو الحكم المتعلق به.",
            "answer": f"انظر إلى المثال، وحدد الكلمة المقصودة، ثم اربطها بـ`{first}` قبل ذكر الحكم النهائي.",
        },
        {
            "question": f"صنّف `{second_example}` بحسب الباب الذي يدرسه هذا الموضع.",
            "answer": f"التصنيف يكون بالنظر إلى `{third}` ثم بيان السبب؛ لا يكفي ذكر العلامة دون السبب.",
        },
        {
            "question": f"اذكر مثالًا جديدًا يوضح `{second}` ثم بيّن وجه الشاهد فيه.",
            "answer": f"مثال صحيح يكفي إذا ظهر فيه `{second}` بوضوح، ثم تذكر العامل أو الوزن أو العلاقة البلاغية بحسب الباب.",
        },
    ]


def parse_questions(section: str) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    pattern = re.compile(
        r"(?ms)^\s*\d+\.\s+(?P<question>.+?)\n\s*[-*]\s*الجواب:\s*(?P<answer>.+?)(?=^\s*\d+\.|\Z)"
    )
    for index, match in enumerate(pattern.finditer(section), start=1):
        question = re.sub(r"\s+", " ", match.group("question")).strip()
        answer = re.sub(r"\s+", " ", match.group("answer")).strip()
        if question and answer:
            questions.append({"id": f"q{index:02d}", "question": question, "answer": answer})
    return questions


def extract_module_questions(title: str, markdown: str) -> tuple[str, list[dict[str, str]]]:
    heading = re.search(r"^#{3,6}\s+أسئلة التحقق\s*$", markdown, flags=re.MULTILINE)
    if not heading:
        fallback = default_questions(title, markdown)
        return markdown, [{"id": f"q{index:02d}", **question} for index, question in enumerate(fallback, start=1)]

    clean_markdown = markdown[: heading.start()].rstrip()
    quiz_section = markdown[heading.end() :].strip()
    questions = parse_questions(quiz_section)
    if len(questions) < 5:
        existing = {(item["question"], item["answer"]) for item in questions}
        for fallback in default_questions(title, clean_markdown):
            key = (fallback["question"], fallback["answer"])
            if key not in existing:
                questions.append({"id": f"q{len(questions) + 1:02d}", **fallback})
            if len(questions) >= 5:
                break
    return clean_markdown, questions


def split_markdown_h2(markdown: str, prefix: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(markdown))
    modules: list[dict[str, Any]] = []
    intro = markdown[: matches[0].start()].strip() if matches else markdown.strip()
    if intro:
        clean_intro, questions = extract_module_questions("Accueil", intro)
        modules.append(
            {
                "id": f"{prefix}-accueil",
                "title": "Accueil",
                "markdown": clean_intro,
                "excerpt": markdown_excerpt(clean_intro),
                "questions": questions,
            }
        )
    for index, match in enumerate(matches, start=1):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index].start() if index < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        clean_body, questions = extract_module_questions(title, body)
        modules.append(
            {
                "id": f"{prefix}-{index:02d}-{slug(title)}",
                "title": title,
                "markdown": clean_body,
                "excerpt": markdown_excerpt(clean_body),
                "questions": questions,
            }
        )
    return modules


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_audio_manifest() -> dict[tuple[str, str], dict[str, Any]]:
    rows = {}
    for row in read_tsv(AUDIO_MANIFEST):
        rows[(row["identifier"], row["name"])] = {
            "compressed_size_bytes": int(row["compressed_size_bytes"]),
            "path": row["path"],
        }
    return rows


def load_inventory(identifier: str) -> list[AudioRow]:
    rows = []
    for row in read_tsv(ARCHIVE_DIR / identifier / "inventory.tsv"):
        rows.append(
            AudioRow(
                name=row["name"],
                length_seconds=float(row["length_seconds"] or 0),
                source_size_bytes=int(row["size_bytes"] or 0),
                url=row["url"],
            )
        )
    return rows


def parse_transcript_markdown(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    confidence = None
    duration = None
    for line in text.splitlines()[:12]:
        if line.startswith("- confidence:"):
            confidence = line.split(":", 1)[1].strip().strip("`")
        elif line.startswith("- duration:"):
            duration = line.split(":", 1)[1].strip().strip("`")

    body = ""
    if "## Transcription" in text:
        body = text.split("## Transcription", 1)[1]
        body = body.split("## Segments", 1)[0].strip()
    preview = re.sub(r"\s+", " ", body).strip()[:420]
    segment_count = 0
    if "## Segments" in text:
        segment_count = sum(1 for line in text.split("## Segments", 1)[1].splitlines() if line.startswith("["))

    return {
        "confidence": float(confidence) if confidence not in {None, "", "None"} else None,
        "duration": float(duration) if duration not in {None, "", "None"} else None,
        "preview": preview,
        "word_count": len(body.split()),
        "segment_count": segment_count,
    }


def title_from_metadata(identifier: str) -> str:
    metadata = json.loads((ARCHIVE_DIR / identifier / "metadata.json").read_text(encoding="utf-8"))
    return metadata.get("metadata", {}).get("title") or identifier


def load_pedagogical_modules(identifier: str) -> list[dict[str, Any]]:
    course_path = PEDAGOGICAL_DIR / identifier / "cours.md"
    if not course_path.exists():
        return []
    markdown = course_path.read_text(encoding="utf-8")
    modules = split_markdown_h2(markdown, f"{identifier}-module")
    source_map_path = PEDAGOGICAL_DIR / identifier / "source-map.json"
    if not source_map_path.exists():
        return modules

    source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
    source_modules = {
        module["id"]: module
        for module in source_map.get("modules", [])
        if module.get("id")
    }
    for module in modules:
        source_module = source_modules.get(module["id"], {})
        module["audio_spans"] = [
            {
                "lesson_id": span["lesson_id"],
                "start_seconds": span["start_seconds"],
                "end_seconds": span["end_seconds"],
            }
            for span in source_module.get("audio_spans", [])
            if all(key in span for key in ("lesson_id", "start_seconds", "end_seconds"))
        ]
    return modules


def parse_sources() -> dict[str, dict[str, Any]]:
    current: str | None = None
    item: dict[str, Any] | None = None
    resources: dict[str, dict[str, Any]] = {}

    for raw_line in SOURCES_MD.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        match = re.match(r"^###\s+(.+)$", line)
        if match:
            current = match.group(1).strip()
            resources[current] = {"items": [], "notes": []}
            item = None
            continue
        if not current:
            continue
        if line.startswith("- Note:"):
            resources[current]["notes"].append(line.removeprefix("- Note:").strip())
            item = None
            continue
        if line.startswith("- "):
            item = {"title": line[2:].strip(), "links": []}
            resources[current]["items"].append(item)
            continue
        if item is not None and line.startswith("  - "):
            label, _, value = line[4:].partition(":")
            label = label.strip()
            value = value.strip()
            if label.lower() in {"auteur", "author"}:
                item["author"] = value
                continue
            links = extract_links(value)
            if not links:
                item["links"].append({"label": label, "text": value})
            else:
                for link in links:
                    link["label"] = label
                    item["links"].append(link)
    return resources


def extract_links(value: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for url in re.findall(r"https?://\S+", value):
        links.append({"kind": "url", "href": url.rstrip(".,)")})
    for path_text in re.findall(r"`([^`]+)`", value):
        path = Path(path_text)
        full: Path | None = None
        if path_text.startswith("livres/"):
            full = ROOT / path_text
            href = rel(full) if full.exists() else path_text
        elif path_text.startswith("/home/"):
            href = path_text
            candidate = Path(path_text)
            if candidate.exists() and ROOT in candidate.parents:
                full = candidate
                href = rel(candidate)
        else:
            href = path_text
        suffix = path.suffix.lower().lstrip(".") or "text"
        link = {"kind": suffix, "href": href, "path": path_text}
        if full and full.exists():
            link.update(viewer_for_path(full, suffix))
        links.append(link)
    return links


def viewer_for_path(path: Path, suffix: str) -> dict[str, str]:
    if suffix == "pdf":
        return {"viewer_kind": "pdf", "viewer_href": rel(path)}
    if suffix == "html":
        pdf_sibling = path.with_suffix(".pdf")
        if pdf_sibling.exists():
            return {"viewer_kind": "pdf", "viewer_href": rel(pdf_sibling)}
        return {"viewer_kind": "html", "viewer_href": rel(path)}
    if suffix == "md":
        pdf_sibling = path.with_suffix(".pdf")
        if pdf_sibling.exists():
            return {"viewer_kind": "pdf", "viewer_href": rel(pdf_sibling)}
        for html_candidate in (path.with_suffix(".html"), path.parent / "book.html", path.parent / "index.html"):
            if html_candidate.exists():
                pdf_candidate = html_candidate.with_suffix(".pdf")
                if pdf_candidate.exists():
                    return {"viewer_kind": "pdf", "viewer_href": rel(pdf_candidate)}
                return {"viewer_kind": "html", "viewer_href": rel(html_candidate)}
        return {"viewer_kind": "md", "viewer_href": rel(path)}
    if suffix == "txt":
        return {"viewer_kind": "txt", "viewer_href": rel(path)}
    if suffix == "doc":
        pdf_sibling = path.with_suffix(".pdf")
        if pdf_sibling.exists():
            return {"viewer_kind": "pdf", "viewer_href": rel(pdf_sibling)}
        text_sibling = path.with_suffix(".txt")
        if text_sibling.exists():
            return {"viewer_kind": "txt", "viewer_href": rel(text_sibling)}
    return {}


def build_catalog() -> dict[str, Any]:
    audio_manifest = load_audio_manifest()
    source_resources = parse_sources()
    courses = []

    for item_dir in sorted(
        ARCHIVE_DIR.iterdir(),
        key=lambda path: (
            GROUP_ORDER.get(COURSE_GROUPS.get(path.name, ("Autre", 999))[0], 99),
            COURSE_GROUPS.get(path.name, ("Autre", 999))[1],
            path.name,
        ),
    ):
        if not item_dir.is_dir() or not (item_dir / "inventory.tsv").exists():
            continue
        identifier = item_dir.name
        group, order = COURSE_GROUPS.get(identifier, ("Autre", 999))
        lessons = []
        inventory = load_inventory(identifier)
        for index, audio in enumerate(inventory, start=1):
            transcript_candidates = sorted((item_dir / "transcriptions-deepgram").glob(f"{index:03d}-*.md"))
            if not transcript_candidates:
                raise FileNotFoundError(f"transcription absente: {identifier} #{index}")
            transcript_path = transcript_candidates[0]
            transcript_meta = parse_transcript_markdown(transcript_path)
            audio_info = audio_manifest.get((identifier, audio.name))
            if not audio_info:
                raise FileNotFoundError(f"audio compresse absent: {identifier}/{audio.name}")
            lesson_stem = Path(audio.name).stem
            lessons.append(
                {
                    "id": f"{index:03d}-{lesson_stem}",
                    "index": index,
                    "title": f"Cours {index}",
                    "source_name": audio.name,
                    "duration_seconds": audio.length_seconds,
                    "duration_label": seconds_to_label(audio.length_seconds),
                    "source_size_bytes": audio.source_size_bytes,
                    "source_url": audio.url,
                    "audio_path": rel(ROOT / audio_info["path"]),
                    "compressed_size_bytes": audio_info["compressed_size_bytes"],
                    "transcript_path": rel(transcript_path),
                    **transcript_meta,
                }
            )

        total_seconds = sum(lesson["duration_seconds"] for lesson in lessons)
        courses.append(
            {
                "id": identifier,
                "title": title_from_metadata(identifier),
                "group": group,
                "order": order,
                "modules": load_pedagogical_modules(identifier),
                "lesson_count": len(lessons),
                "duration_seconds": total_seconds,
                "duration_label": seconds_to_label(total_seconds),
                "transcript_word_count": sum(lesson["word_count"] for lesson in lessons),
                "resources": source_resources.get(identifier, {"items": [], "notes": []}),
                "lessons": lessons,
            }
        )

    courses.sort(key=lambda course: (GROUP_ORDER.get(course["group"], 99), course["order"], course["id"]))
    total_lessons = sum(course["lesson_count"] for course in courses)
    total_seconds = sum(course["duration_seconds"] for course in courses)
    return {
        "generated_from": "archive-items + audios-opus + livres/sources.md",
        "course_count": len(courses),
        "lesson_count": total_lessons,
        "duration_seconds": total_seconds,
        "duration_label": seconds_to_label(total_seconds),
        "courses": courses,
    }


def main() -> None:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    catalog = build_catalog()
    out = SITE_DATA / "catalog.json"
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"catalog={out.relative_to(ROOT)}")
    print(f"courses={catalog['course_count']} lessons={catalog['lesson_count']} duration={catalog['duration_label']}")


if __name__ == "__main__":
    main()
