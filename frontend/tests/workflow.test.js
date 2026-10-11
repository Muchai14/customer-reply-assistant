import test from 'node:test';
import assert from 'node:assert/strict';
import {DraftState} from '../state.js';
import {createApi} from '../api.js';
const matched = {question: 'refund', source: {id: 'faq-103'}};
test('requires a generated result, reviewed content, and unchanged question', () => {
  const state = new DraftState();
  assert.equal(state.canSave('refund', 'answer'), false);
  state.accept(matched);
  assert.equal(state.canSave('refund', '   '), false);
  assert.equal(state.canSave('changed question', 'answer'), false);
  assert.equal(state.canSave(' refund ', 'answer'), true);
  state.invalidate();
  assert.equal(state.canSave('refund', 'answer'), false);
});
test('manual reply carries no FAQ reference', () => {
  const state = new DraftState(); state.accept({question: 'help', source: null});
  assert.deepEqual(state.payload(' help ', ' answer '), {question: 'help', reply: 'answer', faq_id: null});
  assert.equal(state.canSave('help', 'answer'), true);
});
test('blocks duplicate and in-flight saves; edits permit a new record', () => {
  const state = new DraftState(); state.accept(matched); state.busy = true;
  assert.equal(state.canSave('refund', 'answer'), false);
  state.busy = false; state.markSaved('refund', 'answer');
  assert.equal(state.canSave('refund', ' answer '), false);
  assert.equal(state.canSave('refund', 'edited answer'), true);
  assert.equal(state.canSave('refund', 'x'.repeat(5001)), false);
});
test('API client sends the agreed paths and JSON', async () => {
  const calls = [];
  const api = createApi(async (...args) => { calls.push(args); return {ok: true, json: async () => ({ok: true})}; });
  await api.draft('refund'); await api.save({question:'refund',reply:'answer',faq_id:null});
  await api.history(5, 10); await api.reply(3);
  assert.deepEqual(calls.map(c => c[0]), ['/api/drafts','/api/replies','/api/replies?limit=5&offset=10','/api/replies/3']);
  assert.equal(calls[0][1].method, 'POST');
  assert.deepEqual(JSON.parse(calls[0][1].body), {question:'refund'});
  assert.equal(calls[0][1].headers['Content-Type'], 'application/json');
});
test('API client explains validation and network errors', async () => {
  const invalid = createApi(async () => ({ok:false,status:422,json:async()=>({detail:[{msg:'Question must not be blank.'}]})}));
  await assert.rejects(invalid.draft(''), /Question must not be blank/);
  const offline = createApi(async () => { throw new Error('offline'); });
  await assert.rejects(offline.history(5,0), /Your text is still here/);
  const broken = createApi(async () => ({ok:false,status:500,json:async()=>{throw new Error('not json');}}));
  await assert.rejects(broken.save({}), /Request failed \(500\)/);
});
