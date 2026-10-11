// Prevent saving a reply against a changed question or saving it twice unchanged.
export class DraftState {
  constructor() { this.reset(); }
  reset() { this.question = null; this.faqId = null; this.saved = null; this.busy = false; }
  accept(result) { this.question = result.question; this.faqId = result.source?.id ?? null; this.saved = null; }
  invalidate() { this.question = null; this.faqId = null; this.saved = null; }
  payload(question, reply) { return {question: question.trim(), reply: reply.trim(), faq_id: this.faqId}; }
  canSave(question, reply) {
    const payload = this.payload(question, reply);
    return !this.busy && this.question !== null && payload.question === this.question &&
      payload.question.length > 0 && payload.question.length <= 1000 &&
      payload.reply.length > 0 && payload.reply.length <= 5000 && JSON.stringify(payload) !== this.saved;
  }
  markSaved(question, reply) { this.saved = JSON.stringify(this.payload(question, reply)); }
}
