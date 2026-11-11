// Human Override (c) 2026 Amghar Said - tests for the paste guard detector. Run: node --test human-override/test/
const test = require('node:test');
const assert = require('node:assert');
const { scan, mask } = require('../extension/detect.js');
const kinds = (t, w) => [...new Set(scan(t, w).map(f => f.kind))].sort();

test('finds a valid IBAN with or without spaces', () => {
  assert.deepStrictEqual(kinds('Pay to BE71 0961 2345 6769 please'), ['iban']);
  assert.deepStrictEqual(kinds('NL91ABNA0417164300'), ['iban']);
});
test('finds an IBAN when other text or another IBAN follows it', () => {
  assert.deepStrictEqual(kinds('IBAN BE71 0961 2345 6769 BIC GEBABEBB'), ['iban']);
  assert.strictEqual(mask('BE71 0961 2345 6769 NL91 ABNA 0417 1643 00 2024 OK'), '[IBAN] [IBAN] 2024 OK');
  assert.deepStrictEqual(kinds('Morocco MA64 0115 1900 0001 2050 0053 4921 thanks'), ['iban']);
});
test('ignores an IBAN with a wrong check number', () => {
  assert.deepStrictEqual(kinds('BE72 0961 2345 6769'), []);
});
test('finds a card number only when the Luhn check passes', () => {
  assert.deepStrictEqual(kinds('card 4111 1111 1111 1111 exp 12/29'), ['card']);
  assert.deepStrictEqual(kinds('order 4111 1111 1111 1112'), []);
});
test('one email is fine, two or more is a list of personal data', () => {
  assert.deepStrictEqual(kinds('mail me at jan@example.com'), []);
  assert.deepStrictEqual(kinds('jan@example.com, piet@example.org'), ['email']);
});
test('finds secret keys and private keys', () => {
  // fake keys are glued together at run time, so secret scanners do not flag this test file
  assert.deepStrictEqual(kinds('key = ' + 'sk-' + 'proj-' + 'abcdefghijklmnopqrstuvwxyz123456'), ['secret']);
  assert.deepStrictEqual(kinds('AKIA' + 'IOSFODNN7' + 'EXAMPLE'), ['secret']);
  assert.deepStrictEqual(kinds('-----BEGIN RSA ' + 'PRIVATE KEY-----\nMIIE'), ['secret']);
});
test('finds confidential markers in EN, NL and FR', () => {
  assert.deepStrictEqual(kinds('CONFIDENTIAL - do not share'), ['label']);
  assert.deepStrictEqual(kinds('Dit document is vertrouwelijk.'), ['label']);
  assert.deepStrictEqual(kinds('Usage interne uniquement'), ['label']);
});
test('finds a Belgian national register number with a valid check', () => {
  assert.deepStrictEqual(kinds('RRN 85.07.30-033.28'), ['id']);
  assert.deepStrictEqual(kinds('RRN 85.07.30-033.29'), []);
});
test('normal text is clean', () => {
  assert.deepStrictEqual(kinds('Write a poem about the sea in 2026, about 120 words.'), []);
  assert.deepStrictEqual(kinds(''), []);
});
test('mask replaces only the sensitive parts', () => {
  const t = 'IBAN BE71 0961 2345 6769, mails a@x.be b@y.be';
  assert.strictEqual(mask(t), 'IBAN [IBAN], mails [EMAIL] [EMAIL]');
});
test('text too long to check is flagged, so padding cannot sneak data past', () => {
  const t = 'x'.repeat(300000) + ' BE71 0961 2345 6769';
  assert.deepStrictEqual(kinds(t), ['long']);
});
test('crafted text with many matches stays fast', () => {
  const t = 'a@b.co confidential '.repeat(9000);
  const t0 = Date.now(); scan(t); mask(t);
  assert.ok(Date.now() - t0 < 1500, 'took ' + (Date.now() - t0) + ' ms');
});

// ---- own private words (1.1.0) ----
test('finds an own private word, whatever the capitals', () => {
  assert.deepStrictEqual(kinds('Status of project Zeus-42 please', ['zeus-42']), ['custom']);
  assert.deepStrictEqual(kinds('status of PROJECT ZEUS-42', ['Project Zeus-42']), ['custom']);
});
test('own words do nothing when the text does not contain them', () => {
  assert.deepStrictEqual(kinds('Write a poem about the sea', ['zeus-42', 'acme corp']), []);
});
test('own words that are too short, too long or not text are ignored', () => {
  assert.deepStrictEqual(kinds('ab abc', ['ab', '', null, 42, 'x'.repeat(61)]), []);
});
test('special characters in an own word are taken literally', () => {
  assert.deepStrictEqual(kinds('ref (a+b)*c.d here', ['(a+b)*c.d']), ['custom']);
  assert.deepStrictEqual(kinds('ref aab c d here', ['(a+b)*c.d']), []);
});
test('mask hides own words and keeps the rest', () => {
  assert.strictEqual(mask('Client Acme Corp owes us, IBAN BE71 0961 2345 6769', ['acme corp']), 'Client [PRIVATE] owes us, IBAN [IBAN]');
});
test('positions stay exact when a letter changes length in lower case', () => {
  assert.strictEqual(mask('İİİ client ACME Corp here', ['acme corp']), 'İİİ client [PRIVATE] here');
});
test('a longer own word wins over a shorter one inside it', () => {
  assert.strictEqual(mask('about project zeus today', ['zeus', 'project zeus']), 'about [PRIVATE] today');
});
test('when a limit is reached the result says so, so nothing is pasted half-masked', () => {
  const t = 'zeus '.repeat(600);
  assert.ok(kinds(t, ['zeus']).includes('long'));
  const many = 'BE71 0961 2345 6769 '.repeat(600);
  assert.ok(kinds(many).includes('long'));
});
test('many own words and many hits stay fast', () => {
  const words = Array.from({ length: 100 }, (_, i) => 'secret' + i);
  const t = 'secret7 and secret99 lorem ipsum '.repeat(5000);
  const t0 = Date.now(); scan(t, words); mask(t, words);
  assert.ok(Date.now() - t0 < 1500, 'took ' + (Date.now() - t0) + ' ms');
});
