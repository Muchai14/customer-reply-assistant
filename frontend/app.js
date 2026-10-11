import {api} from './api.js';
import {DraftState} from './state.js';
const $ = id => document.getElementById(id);
const question = $('question'), reply = $('reply'), state = new DraftState();
let offset = 0, total = 0, historyLoading = false, historyRequest = 0, detailRequest = 0;
const pageSize = 5;
function status(id, message, kind = '') { $(id).textContent = message; $(id).className = `status ${kind}`; }
function controls() {
  $('question-count').textContent = `${question.value.length} / 1,000`;
  $('reply-count').textContent = `${reply.value.length} / 5,000`;
  question.disabled = state.busy;
  reply.disabled = state.busy || state.question === null;
  $('generate').disabled = state.busy || !question.value.trim();
  $('save').disabled = !state.canSave(question.value, reply.value);
  document.querySelectorAll('[data-question]').forEach(button => { button.disabled = state.busy; });
}
question.addEventListener('input', () => {
  state.invalidate(); $('source').hidden = true; $('draft-badge').textContent = 'AWAITING QUESTION';
  status('draft-status', 'Generate a draft for this question before reviewing and saving.');
  status('save-status', ''); controls();
});
reply.addEventListener('input', () => { status('save-status', ''); controls(); });
document.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => {
  question.value = button.dataset.question; question.dispatchEvent(new Event('input')); question.focus();
}));
$('question-form').addEventListener('submit', async event => {
  event.preventDefault(); if (state.busy || !question.value.trim()) return;
  state.invalidate(); state.busy = true; controls(); $('source').hidden = true;
  status('save-status', ''); status('draft-status', 'Finding a matching FAQ…'); $('draft-badge').textContent = 'LOOKING UP';
  try {
    const result = await api.draft(question.value.trim());
    state.accept(result); question.value = result.question; reply.value = result.draft;
    $('draft-badge').textContent = result.matched ? 'SOURCE FOUND' : 'MANUAL REPLY';
    status('draft-status', result.matched ? 'Draft ready. Check the source and edit the reply before saving.' : result.message);
    if (result.source) {
      $('source-title').textContent = `${result.source.id} · ${result.source.title}`;
      $('source-answer').textContent = result.source.answer;
      $('source').hidden = false; $('source').open = true;
    }
  } catch (error) { status('draft-status', error.message, 'error'); $('draft-badge').textContent = 'TRY AGAIN'; }
  finally { state.busy = false; controls(); }
});
$('save').addEventListener('click', async () => {
  if (!state.canSave(question.value, reply.value)) return;
  state.busy = true; controls(); status('save-status', 'Saving your reviewed reply…');
  try {
    const saved = await api.save(state.payload(question.value, reply.value));
    state.markSaved(question.value, reply.value);
    status('save-status', `Reply #${saved.id} saved. Editing and saving again creates a new record.`, 'success');
    await loadHistory(0);
  } catch (error) { status('save-status', `${error.message} If the connection dropped, refresh history before retrying to check whether it was saved.`, 'error'); }
  finally { state.busy = false; controls(); }
});
function dateText(date) { return new Intl.DateTimeFormat('en', {dateStyle: 'medium', timeStyle: 'short', timeZone: 'UTC'}).format(new Date(date)) + ' UTC'; }
function pageControls() {
  $('previous').disabled = historyLoading || offset === 0;
  $('next').disabled = historyLoading || offset + pageSize >= total;
  $('refresh').disabled = historyLoading;
}
async function loadHistory(target = offset) {
  const requestId = ++historyRequest; historyLoading = true; pageControls(); status('history-status', 'Loading replies…');
  try {
    const result = await api.history(pageSize, target);
    if (requestId !== historyRequest) return;
    offset = target; total = result.total; $('total').textContent = total;
    $('history-list').replaceChildren(); $('history-empty').hidden = total !== 0;
    for (const record of result.items) {
      const li = document.createElement('li'), button = document.createElement('button');
      button.type = 'button'; button.className = 'record-button';
      const title = document.createElement('strong'), meta = document.createElement('span');
      title.textContent = record.question; meta.textContent = `#${record.id} · ${dateText(record.created_at)}`;
      button.append(title, meta); button.addEventListener('click', () => openRecord(record.id)); li.append(button); $('history-list').append(li);
    }
    $('page-label').textContent = total ? `${offset + 1}–${offset + result.items.length} of ${total}` : '0 replies';
    status('history-status', '');
  } catch (error) { if (requestId === historyRequest) status('history-status', error.message, 'error'); }
  finally { if (requestId === historyRequest) { historyLoading = false; pageControls(); } }
}
async function openRecord(id) {
  const requestId = ++detailRequest;
  status('history-status', 'Opening saved reply…');
  try {
    const record = await api.reply(id); if (requestId !== detailRequest) return;
    $('record-title').textContent = `Saved reply #${record.id}`;
    $('record-meta').textContent = `${dateText(record.created_at)} · ${record.faq_id || 'Manual reply · no FAQ source'}`;
    $('record-question').textContent = record.question; $('record-reply').textContent = record.reply;
    status('history-status', ''); $('record-dialog').showModal();
  } catch (error) { if (requestId === detailRequest) status('history-status', error.message, 'error'); }
}
$('close-dialog').addEventListener('click', () => $('record-dialog').close());
$('previous').addEventListener('click', () => loadHistory(Math.max(0, offset - pageSize)));
$('next').addEventListener('click', () => loadHistory(offset + pageSize));
$('refresh').addEventListener('click', () => loadHistory(0));
controls(); loadHistory(0);
