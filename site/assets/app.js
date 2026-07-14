const PROGRESS_KEY = "cours-arabe-progress-v1";

const state = {
  catalog: null,
  courses: [],
  selectedCourseId: null,
  selectedLessonId: null,
  selectedModuleId: null,
  selectedAudioStartSeconds: 0,
  audioRenderVersion: 0,
  activeTab: "course",
  query: "",
  progress: loadProgress(),
  openAnswers: {},
  transcriptCache: new Map(),
  transcriptRenderVersion: 0,
};

const els = {
  workspace: document.querySelector("#workspace"),
  backHomeButton: document.querySelector("#backHomeButton"),
  courseDoneButton: document.querySelector("#courseDoneButton"),
  moduleDoneButton: document.querySelector("#moduleDoneButton"),
  homeStats: document.querySelector("#homeStats"),
  homeGrid: document.querySelector("#homeGrid"),
  totalStats: document.querySelector("#totalStats"),
  searchInput: document.querySelector("#searchInput"),
  courseGroup: document.querySelector("#courseGroup"),
  courseTitle: document.querySelector("#courseTitle"),
  courseStats: document.querySelector("#courseStats"),
  moduleGrid: document.querySelector("#moduleGrid"),
  lessonCourse: document.querySelector("#lessonCourse"),
  moduleTitle: document.querySelector("#moduleTitle"),
  moduleProgress: document.querySelector("#moduleProgress"),
  lessonSelect: document.querySelector("#lessonSelect"),
  sourceLink: document.querySelector("#sourceLink"),
  audioPlayer: document.querySelector("#audioPlayer"),
  courseContent: document.querySelector("#courseContent"),
  quizList: document.querySelector("#quizList"),
  transcriptMeta: document.querySelector("#transcriptMeta"),
  transcriptText: document.querySelector("#transcriptText"),
  segmentList: document.querySelector("#segmentList"),
  resourceList: document.querySelector("#resourceList"),
  tabs: [...document.querySelectorAll(".tab")],
  panels: {
    course: document.querySelector("#courseTab"),
    quiz: document.querySelector("#quizTab"),
    transcript: document.querySelector("#transcriptTab"),
    segments: document.querySelector("#segmentsTab"),
    resources: document.querySelector("#resourcesTab"),
  },
  themeToggle: document.querySelector("#themeToggle"),
};

const HARAKAT_RULES = [
  ["لا النافية للجنس", "لَا النَّافِيَةُ لِلْجِنْسِ"],
  ["شرح المقدمة الآجرومية", "شَرْحُ الْمُقَدِّمَةِ الْآجُرُّومِيَّةِ"],
  ["المقدمة الآجرومية", "الْمُقَدِّمَةُ الْآجُرُّومِيَّةُ"],
  ["متممة الآجرومية", "مُتَمِّمَةُ الْآجُرُّومِيَّةِ"],
  ["المتممة", "الْمُتَمِّمَةُ"],
  ["الآجرومية", "الْآجُرُّومِيَّةُ"],
  ["قطر الندى", "قَطْرُ النَّدَى"],
  ["محمود الشافعي", "مَحْمُودٍ الشَّافِعِيِّ"],
  ["المبتدئين", "الْمُبْتَدِئِينَ"],
  ["كان وأخواتها", "كَانَ وَأَخَوَاتُهَا"],
  ["إن وأخواتها", "إِنَّ وَأَخَوَاتُهَا"],
  ["ظن وأخواتها", "ظَنَّ وَأَخَوَاتُهَا"],
  ["نائب الفاعل", "نَائِبُ الْفَاعِلِ"],
  ["المفعول به", "الْمَفْعُولُ بِهِ"],
  ["المفعول المطلق", "الْمَفْعُولُ الْمُطْلَقُ"],
  ["المفعول فيه", "الْمَفْعُولُ فِيهِ"],
  ["المفعول لأجله", "الْمَفْعُولُ لِأَجْلِهِ"],
  ["المفعول معه", "الْمَفْعُولُ مَعَهُ"],
  ["جمع المذكر السالم", "جَمْعُ الْمُذَكَّرِ السَّالِمِ"],
  ["جمع المؤنث السالم", "جَمْعُ الْمُؤَنَّثِ السَّالِمِ"],
  ["الممنوع من الصرف", "الْمَمْنُوعُ مِنَ الصَّرْفِ"],
  ["الأسماء الخمسة", "الْأَسْمَاءُ الْخَمْسَةُ"],
  ["الأفعال الخمسة", "الْأَفْعَالُ الْخَمْسَةُ"],
  ["الكلام", "الْكَلَامُ"],
  ["الإعراب", "الْإِعْرَابُ"],
  ["العامل", "الْعَامِلُ"],
  ["معرب", "مُعْرَبٌ"],
  ["مبني", "مَبْنِيٌّ"],
  ["الرفع", "الرَّفْعُ"],
  ["النصب", "النَّصْبُ"],
  ["الخفض", "الْخَفْضُ"],
  ["الجر", "الْجَرُّ"],
  ["الجزم", "الْجَزْمُ"],
  ["الفاعل", "الْفَاعِلُ"],
  ["المبتدأ", "الْمُبْتَدَأُ"],
  ["الخبر", "الْخَبَرُ"],
  ["الحال", "الْحَالُ"],
  ["التمييز", "التَّمْيِيزُ"],
  ["المنادى", "الْمُنَادَى"],
  ["الاستثناء", "الِاسْتِثْنَاءُ"],
  ["المجرورات", "الْمَجْرُورَاتُ"],
  ["التوابع", "التَّوَابِعُ"],
  ["النعت", "النَّعْتُ"],
  ["العطف", "الْعَطْفُ"],
  ["التوكيد", "التَّوْكِيدُ"],
  ["البدل", "الْبَدَلُ"],
  ["النكرة", "النَّكِرَةُ"],
  ["المعرفة", "الْمَعْرِفَةُ"],
  ["بدل كل من كل", "بَدَلُ كُلٍّ مِنْ كُلٍّ"],
  ["بدل بعض من كل", "بَدَلُ بَعْضٍ مِنْ كُلٍّ"],
  ["بدل اشتمال", "بَدَلُ اشْتِمَالٍ"],
  ["بدل الغلط", "بَدَلُ الْغَلَطِ"],
  ["جاء زيدٌ", "جَاءَ زَيْدٌ"],
  ["رأيت زيدًا", "رَأَيْتُ زَيْدًا"],
  ["مررت بزيدٍ", "مَرَرْتُ بِزَيْدٍ"],
  ["قام زيدٌ", "قَامَ زَيْدٌ"],
  ["قرأ الطالبُ الدرسَ", "قَرَأَ الطَّالِبُ الدَّرْسَ"],
  ["جاء الطالب المجتهد", "جَاءَ الطَّالِبُ الْمُجْتَهِدُ"],
  ["حضر الطلاب كلهم", "حَضَرَ الطُّلَّابُ كُلُّهُمْ"],
  ["قرأت الكتاب مقدمته", "قَرَأْتُ الْكِتَابَ مُقَدِّمَتَهُ"],
  ["أحببت زيدًا علمه", "أَحْبَبْتُ زَيْدًا عِلْمَهُ"],
  ["لا رجلَ في الدار", "لَا رَجُلَ فِي الدَّارِ"],
  ["يا زيدُ", "يَا زَيْدُ"],
  ["يا عبدَ الله", "يَا عَبْدَ اللهِ"],
  ["لم يقرأْ الولدُ الكتابَ في البيتِ", "لَمْ يَقْرَأْ الْوَلَدُ الْكِتَابَ فِي الْبَيْتِ"],
  ["لم يقرأ الولد الكتاب في البيت", "لَمْ يَقْرَأْ الْوَلَدُ الْكِتَابَ فِي الْبَيْتِ"],
].sort((a, b) => b[0].length - a[0].length);

init().catch((error) => {
  document.body.innerHTML = `<main class="error">Erreur chargement interface: ${escapeHtml(error.message)}</main>`;
});

async function init() {
  const response = await fetch("data/catalog.json");
  if (!response.ok) {
    throw new Error(`catalog.json HTTP ${response.status}`);
  }
  state.catalog = await response.json();
  state.courses = state.catalog.courses;
  state.selectedCourseId = null;
  state.selectedLessonId = null;
  state.selectedModuleId = null;

  els.searchInput.addEventListener("input", () => {
    state.query = els.searchInput.value.trim();
    renderHome();
    if (state.selectedCourseId) {
      renderActiveLesson();
    }
  });

  els.backHomeButton.addEventListener("click", () => {
    state.selectedCourseId = null;
    state.selectedLessonId = null;
    state.selectedModuleId = null;
    state.selectedAudioStartSeconds = 0;
    state.activeTab = "course";
    render();
  });

  els.courseDoneButton.addEventListener("click", toggleCourseDone);
  els.moduleDoneButton.addEventListener("click", toggleModuleDone);
  els.lessonSelect.addEventListener("change", () => {
    state.selectedLessonId = els.lessonSelect.value;
    state.selectedAudioStartSeconds = 0;
    renderActiveLesson();
  });

  els.tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      state.activeTab = tab.dataset.tab;
      renderTabs();
    });
  });

  els.themeToggle.addEventListener("click", toggleTheme);

  initTheme();
  render();
}

const THEME_KEY = "cours-arabe-theme-v1";

function initTheme() {
  let theme = localStorage.getItem(THEME_KEY);
  if (!theme) {
    theme = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  document.documentElement.setAttribute("data-theme", theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  try {
    localStorage.setItem(THEME_KEY, next);
  } catch (e) {
    // Ignore storage errors
  }
}

function render() {
  els.totalStats.innerHTML = [
    pill(`${state.catalog.course_count} cours`),
    pill(`${state.catalog.lesson_count} audios`),
    pill(state.catalog.duration_label),
  ].join("");
  renderViewMode();
  renderHome();
  if (state.selectedCourseId) {
    renderCourse();
  }
}

function renderHome() {
  const query = normalize(state.query);
  const courses = state.courses.filter((course) => courseMatches(course, query));
  const doneCount = courses.filter((course) => isCourseDone(course)).length;
  els.homeStats.innerHTML = [
    pill(`${doneCount}/${courses.length} cours faits`),
    pill(`${courses.reduce((total, course) => total + (courseProgress(course).done || 0), 0)} modules faits`),
  ].join("");

  els.homeGrid.innerHTML = "";
  if (!courses.length) {
    els.homeGrid.innerHTML = `<p class="empty">Aucun cours trouve.</p>`;
    return;
  }

  const fragment = document.createDocumentFragment();
  for (const course of courses) {
    const firstPreview = course.modules?.find((module) => module.excerpt)?.excerpt ?? course.lessons.find((lesson) => lesson.preview)?.preview ?? "";
    const tile = document.createElement("button");
    tile.type = "button";
    tile.className = `course-tile${isCourseDone(course) ? " is-done" : ""}`;
    const progress = courseProgress(course);
    tile.innerHTML = `
      <span class="course-tile-top">
        <span class="course-tile-badges">
          <span class="course-tile-badge" data-group="${escapeAttribute(course.group)}">${escapeHtml(course.group)}</span>
          <span class="course-tile-stat">${course.lesson_count} leçons</span>
          <span class="course-tile-stat">${progress.label}</span>
        </span>
        <h3>${highlight(applyHarakat(course.title), state.query)}</h3>
        <span class="course-tile-preview" dir="rtl" lang="ar">${highlight(applyHarakat(firstPreview), state.query)}</span>
      </span>
      <span class="course-tile-bottom">
        <span class="progress-track" aria-hidden="true"><span style="width: ${progress.percent}%"></span></span>
        <span class="course-tile-stats">
          <span class="course-tile-stat">${course.duration_label}</span>
          <span class="course-tile-stat">${formatNumber(course.transcript_word_count)} mots</span>
          <span class="course-tile-stat">${course.resources.items.length} ressources</span>
        </span>
      </span>
    `;
    tile.addEventListener("click", () => openCourse(course));
    fragment.append(tile);
  }
  els.homeGrid.replaceChildren(fragment);
}

function renderCourse() {
  const course = selectedCourse();
  if (!course) {
    renderViewMode();
    return;
  }
  if (!course.modules?.some((module) => module.id === state.selectedModuleId)) {
    state.selectedModuleId = course.modules?.[0]?.id ?? null;
    selectModuleAudio(course, course.modules?.[0]);
  }
  if (!course.lessons.some((lesson) => lesson.id === state.selectedLessonId)) {
    state.selectedLessonId = course.lessons[0]?.id ?? null;
    state.selectedAudioStartSeconds = 0;
  }
  renderViewMode();
  const progress = courseProgress(course);
  els.courseGroup.textContent = course.group;
  els.courseTitle.textContent = applyHarakat(course.title);
  els.courseStats.innerHTML = [
    pill(progress.label),
    pill(`${course.lesson_count} audios`),
    pill(course.duration_label),
  ].join("");
  els.courseDoneButton.textContent = isCourseDone(course) ? "Cours fait" : "Marquer cours fait";
  els.courseDoneButton.classList.toggle("is-done", isCourseDone(course));
  renderModuleTiles(course);
  renderLessonSelect(course);
  renderActiveLesson();
}

function openCourse(course) {
  state.selectedCourseId = course.id;
  state.selectedLessonId = course.lessons[0]?.id ?? null;
  state.selectedModuleId = course.modules?.[0]?.id ?? null;
  selectModuleAudio(course, course.modules?.[0]);
  state.activeTab = preferredTab(course);
  renderCourse();
}

function selectModuleAudio(course, module) {
  const firstSpan = module?.audio_spans?.[0];
  const lesson = firstSpan
    ? course.lessons.find((item) => item.id === firstSpan.lesson_id)
    : null;
  if (!lesson) {
    state.selectedAudioStartSeconds = 0;
    return;
  }
  state.selectedLessonId = lesson.id;
  state.selectedAudioStartSeconds = Number(firstSpan.start_seconds) || 0;
  els.lessonSelect.value = lesson.id;
}

function renderViewMode() {
  const isHome = !state.selectedCourseId;
  els.workspace.classList.toggle("is-home", isHome);
  els.workspace.classList.toggle("is-course", !isHome);
}

function renderModuleTiles(course) {
  const modules = course.modules ?? [];
  els.moduleGrid.innerHTML = "";
  if (!modules.length) {
    els.moduleGrid.innerHTML = `<p class="empty">Aucun module pédagogique structuré.</p>`;
    return;
  }
  for (const [index, module] of modules.entries()) {
    const quiz = questionProgress(course.id, module);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `module-tile${module.id === state.selectedModuleId ? " is-active" : ""}${isModuleDone(course.id, module.id) ? " is-done" : ""}`;
    button.innerHTML = `
        <span class="lesson-number">${index + 1}</span>
      <span class="lesson-main">
        <strong>${escapeHtml(applyHarakat(module.title))}</strong>
        <span class="lesson-meta">
          <span>Module ${index + 1}</span>
          <span>${isModuleDone(course.id, module.id) ? "fait" : "à faire"}</span>
          <span>${quiz.label}</span>
        </span>
        <span class="lesson-preview" dir="rtl" lang="ar">${highlight(applyHarakat(module.excerpt), state.query)}</span>
      </span>
    `;
    button.addEventListener("click", () => {
      state.selectedModuleId = module.id;
      selectModuleAudio(course, module);
      state.activeTab = "course";
      renderModuleTiles(course);
      renderActiveLesson();
    });
    els.moduleGrid.append(button);
  }
}

function renderLessonSelect(course) {
  els.lessonSelect.innerHTML = "";
  for (const lesson of course.lessons) {
    const option = document.createElement("option");
    option.value = lesson.id;
    option.textContent = `${lesson.index}. ${lesson.duration_label}`;
    option.selected = lesson.id === state.selectedLessonId;
    els.lessonSelect.append(option);
  }
}

async function renderActiveLesson() {
  const course = selectedCourse();
  const lesson = selectedLesson();
  if (!course || !lesson) {
    return;
  }
  const module = selectedModule();
  const progress = courseProgress(course);
  els.lessonCourse.textContent = applyHarakat(course.title);
  els.moduleTitle.textContent = module?.title ?? `${lesson.title} · ${lesson.duration_label}`;
  els.moduleProgress.textContent = progress.label;
  els.moduleDoneButton.textContent = module && isModuleDone(course.id, module.id) ? "Module fait" : "Marquer module fait";
  els.moduleDoneButton.classList.toggle("is-done", Boolean(module && isModuleDone(course.id, module.id)));
  els.sourceLink.href = lesson.source_url;
  const audioRenderVersion = ++state.audioRenderVersion;
  els.audioPlayer.src = lesson.audio_path;
  const seekToModuleStart = () => {
    if (audioRenderVersion !== state.audioRenderVersion) {
      return;
    }
    const duration = Number.isFinite(els.audioPlayer.duration) ? els.audioPlayer.duration : Infinity;
    els.audioPlayer.currentTime = Math.min(state.selectedAudioStartSeconds, duration);
  };
  if (els.audioPlayer.readyState >= HTMLMediaElement.HAVE_METADATA) {
    seekToModuleStart();
  } else {
    els.audioPlayer.addEventListener("loadedmetadata", seekToModuleStart, { once: true });
  }
  els.transcriptMeta.innerHTML = [
    pill(confidenceLabel(lesson.confidence)),
    pill(`${formatNumber(lesson.word_count)} mots`),
    pill(`${lesson.segment_count} segments`),
    pill(lesson.source_name),
  ].join("");

  renderResources(course);
  renderCourseContent(course);
  renderQuiz(course);
  renderTabs();
  await loadAndRenderTranscript(lesson);
}

function preferredTab(course) {
  return course?.modules?.length ? "course" : "transcript";
}

function renderCourseContent(course) {
  const modules = course.modules ?? [];
  const module = selectedModule();
  if (!modules.length) {
    els.courseContent.innerHTML = `
      <p class="empty">
        Aucun cours pédagogique structuré pour ce livre. Utilise la transcription brute et les ressources Matn / Charh en attendant la synthèse.
      </p>
    `;
    return;
  }

  els.courseContent.innerHTML = `
    <section class="module-card module-card-detail">
      <div class="module-heading">
        <span class="lesson-number">${Math.max(1, modules.findIndex((item) => item.id === module?.id) + 1)}</span>
        <div>
          <p class="eyebrow">Module pédagogique</p>
          <h3>${escapeHtml(applyHarakat(module?.title ?? modules[0].title))}</h3>
        </div>
      </div>
      <div class="markdown-body">${renderMarkdown(module?.markdown ?? modules[0].markdown)}</div>
    </section>
  `;
}

function renderQuiz(course) {
  const module = selectedModule();
  const questions = module?.questions ?? [];
  els.quizList.innerHTML = "";
  if (!module || !questions.length) {
    els.quizList.innerHTML = `<p class="empty">Aucun questionnaire pour ce module.</p>`;
    return;
  }

  const progress = questionProgress(course.id, module);
  const summary = document.createElement("div");
  summary.className = "quiz-summary";
  summary.innerHTML = `
    <div>
      <p class="eyebrow">Questionnaire</p>
      <h3>${escapeHtml(applyHarakat(module.title))}</h3>
    </div>
    <div class="quiz-score">
      <span class="pill">${escapeHtml(progress.label)}</span>
    </div>
  `;
  els.quizList.append(summary);

  for (const [index, question] of questions.entries()) {
    const questionId = question.id || `q${String(index + 1).padStart(2, "0")}`;
    const key = questionKey(course.id, module.id, questionId);
    const open = Boolean(state.openAnswers[key]);
    const article = document.createElement("article");
    article.className = "question-card";
    article.innerHTML = `
      <div class="question-card-top">
        <span class="lesson-number">${index + 1}</span>
        <div class="question-details">
          <div class="question-prompt">${inlineMarkdown(question.question)}</div>
          <div class="question-actions">
            <button class="answer-toggle" type="button">${open ? "Masquer corrigé" : "Voir corrigé"}</button>
          </div>
          ${open ? `<div class="question-answer"><p class="eyebrow">Corrigé</p>${renderMarkdown(question.answer)}</div>` : ""}
        </div>
      </div>
    `;
    article.querySelector(".answer-toggle").addEventListener("click", () => {
      toggleAnswer(course.id, module.id, questionId);
    });
    els.quizList.append(article);
  }
}

async function loadAndRenderTranscript(lesson) {
  const renderVersion = ++state.transcriptRenderVersion;
  els.transcriptText.textContent = "Chargement...";
  els.segmentList.innerHTML = "";
  try {
    const markdown = await getTranscript(lesson);
    if (renderVersion !== state.transcriptRenderVersion) {
      return;
    }
    const transcript = extractTranscript(markdown);
    const segments = extractSegments(markdown);
    els.transcriptText.innerHTML = highlight(applyHarakat(transcript || "Transcription vide."), state.query);
    renderSegments(segments);
  } catch (error) {
    if (renderVersion !== state.transcriptRenderVersion) {
      return;
    }
    els.transcriptText.innerHTML = `<span class="error">${escapeHtml(error.message)}</span>`;
    els.segmentList.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  }
}

async function getTranscript(lesson) {
  if (state.transcriptCache.has(lesson.transcript_path)) {
    return state.transcriptCache.get(lesson.transcript_path);
  }
  const response = await fetch(encodeURI(lesson.transcript_path));
  if (!response.ok) {
    throw new Error(`Transcription HTTP ${response.status}`);
  }
  const markdown = await response.text();
  state.transcriptCache.set(lesson.transcript_path, markdown);
  return markdown;
}

function renderSegments(segments) {
  if (!segments.length) {
    els.segmentList.innerHTML = `<p class="empty">Aucun segment.</p>`;
    return;
  }
  const fragment = document.createDocumentFragment();
  for (const segment of segments) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "segment-button";
    button.innerHTML = `
      <span class="segment-time">${escapeHtml(segment.label)}</span>
      <span>${highlight(applyHarakat(segment.text), state.query)}</span>
    `;
    button.addEventListener("click", () => {
      els.audioPlayer.currentTime = segment.start;
      els.audioPlayer.play().catch(() => {});
    });
    fragment.append(button);
  }
  els.segmentList.replaceChildren(fragment);
}

function renderResources(course) {
  const resources = course.resources ?? { items: [], notes: [] };
  const viewable = viewableResources(resources);
  els.resourceList.innerHTML = "";
  if (!resources.items.length && !resources.notes.length) {
    els.resourceList.innerHTML = `<p class="empty">Aucune ressource locale referencee.</p>`;
    return;
  }
  for (const resource of resources.items) {
    const buttons = consultableResourceButtons(resource, viewable);
    if (!buttons.length) {
      continue;
    }
    const article = document.createElement("article");
    article.className = "resource-item";
    const actions = buttons
      .map(
        (button) =>
          `<a class="resource-viewer-button" href="${escapeAttribute(encodeURI(button.href))}" target="_blank" rel="noreferrer">${escapeHtml(button.label)}</a>`,
      )
      .join("");
    article.innerHTML = `
      <h3>${escapeHtml(resource.title)}</h3>
      <div class="resource-links">${actions}</div>
    `;
    els.resourceList.append(article);
  }
  if (resources.notes.length) {
    const notes = document.createElement("div");
    notes.className = "notes";
    notes.innerHTML = resources.notes.map((note) => `<p>${escapeHtml(note)}</p>`).join("");
    els.resourceList.append(notes);
  }
}

function viewableResources(resources) {
  const items = [];
  for (const resource of resources.items ?? []) {
    for (const link of resource.links ?? []) {
      if (link.viewer_href) {
        items.push({
          title: `${resource.title} · ${link.label}`,
          resourceTitle: resource.title,
          resource,
          link,
          role: classifyBookRole(resource, link),
        });
      }
    }
  }
  return items;
}

function consultableResourceButtons(resource, viewable) {
  const candidates = viewable.filter((item) => item.resource === resource);
  const pdfs = candidates.filter((item) => item.link.viewer_kind === "pdf");
  const selected = pdfs.length ? preferredPdfLinks(pdfs) : [bestBook(candidates)].filter(Boolean);
  return selected.map((item, index) => ({
    index: viewable.indexOf(item),
    href: item.link.viewer_href,
    label: consultButtonLabel(item, selected.length, index),
  }));
}

function preferredPdfLinks(items) {
  const byHref = new Map();
  for (const item of [...items].sort((a, b) => bookScore(a) - bookScore(b))) {
    if (!byHref.has(item.link.viewer_href)) {
      byHref.set(item.link.viewer_href, item);
    }
  }
  const unique = [...byHref.values()];
  const hasVolumes = unique.some((item) => volumeLabel(item));
  const searchable = unique.filter((item) => /recherchable|searchable/.test(normalize(`${item.title} ${item.link.label ?? ""}`)));
  if (!hasVolumes && searchable.length) {
    return searchable;
  }
  if (!hasVolumes && unique.length > 1) {
    return [unique.find((item) => item.link.viewer_href.includes("/livres/pdf/")) ?? unique[0]];
  }
  return unique;
}

function consultButtonLabel(item, total, index) {
  const volume = volumeLabel(item);
  const role = viewerRoleLabel(item.role);
  const author = item.resource?.author ? ` · ${item.resource.author}` : "";
  if (volume) {
    return `Consulter ${role} ${volume}${author}`;
  }
  if (total > 1) {
    return `Consulter ${role} ${index + 1}${author}`;
  }
  return `Consulter ${role}${author}`;
}

function volumeLabel(item) {
  const text = `${item.link.label ?? ""} ${item.link.href ?? ""}`;
  const match = text.match(/\b(?:vol\.?|tome|volume)\s*([0-9]+)/i) ?? text.match(/(?:^|[-_\s])([0-9]+)\.pdf$/i);
  return match ? `vol. ${match[1]}` : "";
}

function bestBook(items) {
  return [...items].sort((a, b) => bookScore(a) - bookScore(b))[0] ?? null;
}

function bookScore(item) {
  const kindScore = {
    pdf: 0,
    html: 10,
    txt: 30,
    md: 40,
  }[item.link.viewer_kind] ?? 50;
  const text = normalize(`${item.title} ${item.link.label ?? ""}`);
  const searchableBonus = /recherchable|searchable/.test(text) ? -2 : 0;
  const ocrPenalty = /ocr/.test(text) ? 8 : 0;
  const scanPenalty = /scan/.test(text) ? 3 : 0;
  return kindScore + searchableBonus + ocrPenalty + scanPenalty;
}

function classifyBookRole(resource, link) {
  const text = normalize(`${resource.title ?? ""} ${link.label ?? ""} ${link.path ?? ""} ${link.href ?? ""}`);
  if (/sharh|charh|شرح|commentaire|explication|principal|alternatif|référence|reference/.test(text)) {
    return "charh";
  }
  if (/matn|متن|source proche|source du cours|livre du cours|نظم|ألفية|لامية|دروس البلاغة|نكت الإعراب/.test(text)) {
    return "matn";
  }
  return "book";
}

function viewerSlotFor(resource) {
  const role = typeof resource === "string" ? resource : resource?.role;
  if (role === "charh") {
    return "charh";
  }
  if (role === "matn") {
    return "matn";
  }
  return "book";
}

function viewerRoleLabel(role) {
  const slot = viewerSlotFor(role);
  if (slot === "charh") {
    return "Charh";
  }
  if (slot === "matn") {
    return "Matn";
  }
  return "Livre";
}

function applyHarakat(value) {
  let text = String(value ?? "");
  for (const [plain, vocalized] of HARAKAT_RULES) {
    const pattern = new RegExp(`(?<![\\u0600-\\u06FF\\u064B-\\u065F])${escapeRegExp(plain)}(?![\\u0600-\\u06FF\\u064B-\\u065F])`, "g");
    text = text.replace(pattern, vocalized);
  }
  return text;
}

function renderMarkdown(markdown) {
  const lines = String(markdown || "").replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    const trimmed = line.trim();
    if (!trimmed) {
      index += 1;
      continue;
    }

    const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      const level = Math.min(6, heading[1].length + 2);
      html.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      index += 1;
      continue;
    }

    if (/^\|/.test(trimmed) && index + 1 < lines.length && /^\|\s*:?-+/.test(lines[index + 1].trim())) {
      const rows = [trimmed];
      index += 2;
      while (index < lines.length && /^\|/.test(lines[index].trim())) {
        rows.push(lines[index].trim());
        index += 1;
      }
      const cells = rows.map((row) =>
        row
          .replace(/^\||\|$/g, "")
          .split("|")
          .map((cell) => cell.trim()),
      );
      const [head, ...body] = cells;
      html.push(
        `<div class="table-wrap"><table><thead><tr>${head
          .map((cell) => `<th>${inlineMarkdown(cell)}</th>`)
          .join("")}</tr></thead><tbody>${body
          .map((row) => `<tr>${row.map((cell) => `<td>${inlineMarkdown(cell)}</td>`).join("")}</tr>`)
          .join("")}</tbody></table></div>`,
      );
      continue;
    }

    if (/^[-*]\s+/.test(trimmed) || /^\d+\.\s+/.test(trimmed)) {
      const ordered = /^\d+\.\s+/.test(trimmed);
      const tag = ordered ? "ol" : "ul";
      const items = [];
      while (index < lines.length) {
        const item = lines[index].trim();
        if (ordered ? !/^\d+\.\s+/.test(item) : !/^[-*]\s+/.test(item)) {
          break;
        }
        items.push(item.replace(/^[-*]\s+/, "").replace(/^\d+\.\s+/, ""));
        index += 1;
      }
      html.push(`<${tag}>${items.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("")}</${tag}>`);
      continue;
    }

    const paragraph = [];
    while (index < lines.length) {
      const current = lines[index].trim();
      if (
        !current ||
        /^#{1,6}\s+/.test(current) ||
        /^[-*]\s+/.test(current) ||
        /^\d+\.\s+/.test(current) ||
        /^\|/.test(current)
      ) {
        break;
      }
      paragraph.push(current);
      index += 1;
    }
    html.push(`<p>${inlineMarkdown(paragraph.join(" "))}</p>`);
  }

  return html.join("");
}

function inlineMarkdown(value) {
  return escapeHtml(applyHarakat(value ?? ""))
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function renderTabs() {
  for (const tab of els.tabs) {
    tab.classList.toggle("is-active", tab.dataset.tab === state.activeTab);
  }
  for (const [name, panel] of Object.entries(els.panels)) {
    panel.classList.toggle("is-active", name === state.activeTab);
  }
}

function loadProgress() {
  if (typeof localStorage === "undefined") {
    return { courses: {}, modules: {}, questions: {} };
  }
  try {
    const parsed = JSON.parse(localStorage.getItem(PROGRESS_KEY) || "{}");
    return {
      courses: parsed.courses && typeof parsed.courses === "object" ? parsed.courses : {},
      modules: parsed.modules && typeof parsed.modules === "object" ? parsed.modules : {},
      questions: parsed.questions && typeof parsed.questions === "object" ? parsed.questions : {},
    };
  } catch {
    return { courses: {}, modules: {}, questions: {} };
  }
}

function saveProgress() {
  if (typeof localStorage === "undefined") {
    return;
  }
  try {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(state.progress));
  } catch {
    // Keep the interface usable if browser storage is blocked.
  }
}

function moduleKey(courseId, moduleId) {
  return `${courseId}::${moduleId}`;
}

function questionKey(courseId, moduleId, questionId) {
  return `${courseId}::${moduleId}::${questionId}`;
}

function isModuleDone(courseId, moduleId) {
  return Boolean(state.progress.modules[moduleKey(courseId, moduleId)]);
}

function isCourseDone(course) {
  if (state.progress.courses[course.id]) {
    return true;
  }
  const modules = course.modules ?? [];
  return Boolean(modules.length && modules.every((module) => isModuleDone(course.id, module.id)));
}

function courseProgress(course) {
  const modules = course.modules ?? [];
  if (!modules.length) {
    return {
      done: isCourseDone(course) ? 1 : 0,
      total: 1,
      percent: isCourseDone(course) ? 100 : 0,
      label: isCourseDone(course) ? "cours fait" : "progression n/a",
    };
  }
  const done = modules.filter((module) => isModuleDone(course.id, module.id)).length;
  return {
    done,
    total: modules.length,
    percent: Math.round((done / modules.length) * 100),
    label: `${done}/${modules.length} modules`,
  };
}

function questionProgress(courseId, module) {
  const questions = module?.questions ?? [];
  if (!questions.length) {
    return { done: 0, total: 0, percent: 0, label: "0 question" };
  }
  return {
    done: 0,
    total: questions.length,
    percent: 100,
    label: `${questions.length} questions`,
  };
}

function toggleModuleDone() {
  const course = selectedCourse();
  const module = selectedModule();
  if (!course || !module) {
    return;
  }
  const key = moduleKey(course.id, module.id);
  state.progress.modules = { ...state.progress.modules, [key]: !state.progress.modules[key] };
  if (!state.progress.modules[key]) {
    delete state.progress.modules[key];
  }
  if (!isCourseDone(course)) {
    delete state.progress.courses[course.id];
  }
  saveProgress();
  render();
}

function toggleAnswer(courseId, moduleId, questionId) {
  const course = selectedCourse();
  const key = questionKey(courseId, moduleId, questionId);
  state.openAnswers = { ...state.openAnswers, [key]: !state.openAnswers[key] };
  if (!state.openAnswers[key]) {
    delete state.openAnswers[key];
  }
  if (course) {
    renderQuiz(course);
  }
}

function toggleCourseDone() {
  const course = selectedCourse();
  if (!course) {
    return;
  }
  const next = !isCourseDone(course);
  state.progress.courses = { ...state.progress.courses, [course.id]: next };
  if (!next) {
    delete state.progress.courses[course.id];
  }
  if (course.modules?.length) {
    state.progress.modules = { ...state.progress.modules };
    for (const module of course.modules) {
      const key = moduleKey(course.id, module.id);
      if (next) {
        state.progress.modules[key] = true;
      } else {
        delete state.progress.modules[key];
      }
    }
  }
  saveProgress();
  render();
}

function selectedCourse() {
  if (!state.selectedCourseId) {
    return null;
  }
  return state.courses.find((course) => course.id === state.selectedCourseId) ?? null;
}

function selectedModule() {
  return selectedCourse()?.modules?.find((module) => module.id === state.selectedModuleId) ?? null;
}

function selectedLesson() {
  return selectedCourse()?.lessons.find((lesson) => lesson.id === state.selectedLessonId);
}

function lessonMatches(lesson, query) {
  if (!query) {
    return true;
  }
  const haystack = normalize(`${lesson.title} ${lesson.source_name} ${lesson.preview}`);
  return haystack.includes(query);
}

function courseMatches(course, query) {
  if (!query) {
    return true;
  }
  const moduleText = (course.modules ?? []).map((module) => `${module.title} ${module.excerpt}`).join(" ");
  const haystack = normalize(`${course.title} ${course.id} ${course.group} ${moduleText}`);
  return haystack.includes(query) || course.lessons.some((lesson) => lessonMatches(lesson, query));
}

function extractTranscript(markdown) {
  if (!markdown.includes("## Transcription")) {
    return markdown.trim();
  }
  const transcriptStart = markdown.indexOf("## Transcription") + "## Transcription".length;
  const segmentsStart = markdown.indexOf("## Segments", transcriptStart);
  const transcriptEnd = segmentsStart === -1 ? markdown.length : segmentsStart;
  return markdown.slice(transcriptStart, transcriptEnd).trim();
}

function extractSegments(markdown) {
  if (!markdown.includes("## Segments")) {
    return [];
  }
  return markdown
    .slice(markdown.indexOf("## Segments") + "## Segments".length)
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("["))
    .map((line) => {
      const match = line.match(/^\[([0-9:]+)\s+-\s+([0-9:]+)\]\s*(.+)$/);
      if (!match) {
        return null;
      }
      return {
        label: `${match[1]} - ${match[2]}`,
        start: timeToSeconds(match[1]),
        end: timeToSeconds(match[2]),
        text: match[3],
      };
    })
    .filter(Boolean);
}

function timeToSeconds(value) {
  const parts = value.split(":").map((part) => Number(part));
  if (parts.length === 2) {
    return parts[0] * 60 + parts[1];
  }
  return parts[0] * 3600 + parts[1] * 60 + parts[2];
}

function confidenceLabel(value) {
  if (typeof value !== "number") {
    return "confiance n/a";
  }
  return `${Math.round(value * 100)}% confiance`;
}

function secondsToLabel(seconds) {
  const total = Math.round(seconds);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  if (hours) {
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  }
  return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function sum(items, key) {
  return items.reduce((total, item) => total + (item[key] ?? 0), 0);
}

function pill(text) {
  return `<span class="pill">${escapeHtml(text)}</span>`;
}

function highlight(value, query) {
  const safe = escapeHtml(value ?? "");
  const normalizedQuery = query.trim();
  if (!normalizedQuery) {
    return safe;
  }
  const escaped = normalizedQuery.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return safe.replace(new RegExp(`(${escaped})`, "giu"), "<mark>$1</mark>");
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalize(value) {
  return (value ?? "")
    .toString()
    .normalize("NFKD")
    .replace(/[\u064B-\u065F\u0670]/g, "")
    .toLowerCase();
}

function formatNumber(value) {
  return new Intl.NumberFormat("fr-FR").format(value ?? 0);
}

function escapeHtml(value) {
  return (value ?? "")
    .toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/`/g, "&#096;");
}
