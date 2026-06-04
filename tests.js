/* Node test harness for the PRISMA 2020 flow + checklist engine.
 * Pure arithmetic — no metafor needed. The reference flow is the worked example
 * from PRISMA 2020 (Page et al., BMJ 2021;372:n71). Run:  node tests.js
 */
var E = require('./engine.js');
var pass = 0, fail = 0;
function ok(name, cond) { if (cond) pass++; else { console.log('FAIL ' + name); fail++; } }
function eq(name, got, want) {
  if (got === want) pass++;
  else { console.log('FAIL ' + name + ': got ' + got + ' want ' + want); fail++; }
}

// A fully consistent flow:
//   db 800, other 200, dup 300  -> screened 700
//   screened 700, excluded 600  -> sought 100
//   sought 100, notRetrieved 10 -> assessed 90
//   assessed 90, excluded reasons (20+15+10=45) -> included 45
var consistent = {
  recordsDb: 800, recordsOther: 200, duplicatesRemoved: 300,
  recordsScreened: 700, recordsExcluded: 600,
  reportsSought: 100, reportsNotRetrieved: 10, reportsAssessed: 90,
  excludedReasons: [
    { reason: 'Wrong population', n: 20 },
    { reason: 'Wrong outcome', n: 15 },
    { reason: 'No control arm', n: 10 }
  ],
  studiesIncluded: 45, reportsIncluded: 50
};

// 1. consistent inputs -> zero warnings
var rc = E.reconcile(consistent);
eq('consistent -> 0 warnings', rc.warnings.length, 0);

// 2. excludedReasons sum
eq('excludedReasons sum', rc.sumExcludedReasons, 45);
eq('sumExcluded helper', E.sumExcluded(consistent.excludedReasons), 45);

// 3-5. derived identities correct
eq('derived screened', rc.derived.recordsScreened, 700);
eq('derived assessed', rc.derived.reportsAssessed, 90);
eq('derived included', rc.derived.studiesIncluded, 45);

// 6. screened mismatch -> exactly one matching warning
var mScreen = E.reconcile(Object.assign({}, consistent, { recordsScreened: 999 }));
ok('screened mismatch warns', mScreen.warnings.some(function (w) { return /Records screened mismatch/.test(w) && /999/.test(w) && /700/.test(w); }));

// 7. assessed mismatch -> matching warning
var mAssess = E.reconcile(Object.assign({}, consistent, { reportsAssessed: 88 }));
ok('assessed mismatch warns', mAssess.warnings.some(function (w) { return /Reports assessed mismatch/.test(w) && /88/.test(w) && /90/.test(w); }));

// 8. included mismatch -> matching warning
var mIncl = E.reconcile(Object.assign({}, consistent, { studiesIncluded: 40 }));
ok('included mismatch warns', mIncl.warnings.some(function (w) { return /Studies included mismatch/.test(w) && /\b40\b/.test(w) && /\b45\b/.test(w); }));

// 9. a single mismatch produces exactly one flow-identity warning (assessed only)
//    (set reportsAssessed inconsistent but keep included consistent with the
//    GIVEN assessed so identity 3 does not also fire)
var oneOnly = E.reconcile(Object.assign({}, consistent, { reportsAssessed: 80, studiesIncluded: 35 }));
eq('isolated assessed mismatch -> 1 warning', oneOnly.warnings.length, 1);

// 10. empty / zero other-sources handled (recordsOther = 0, ?? must keep the 0)
var noOther = E.reconcile({
  recordsDb: 500, recordsOther: 0, duplicatesRemoved: 100,
  recordsScreened: 400
});
eq('recordsOther=0 derived screened', noOther.derived.recordsScreened, 400);
eq('recordsOther=0 no screened warning', noOther.warnings.length, 0);

// 11. recordsOther omitted entirely (null) -> treated as 0 in derivation
var omittedOther = E.reconcile({
  recordsDb: 500, duplicatesRemoved: 100, recordsScreened: 400
});
eq('recordsOther omitted derived screened', omittedOther.derived.recordsScreened, 400);

// 12. partial flow does not throw and yields nulls for unknown derivations
var partial = E.reconcile({ recordsDb: 300 });
ok('partial flow no crash', partial && Array.isArray(partial.warnings));
eq('partial flow derived screened null', partial.derived.recordsScreened, null);

// 13. buildStages produces the included stage with the exclusion-reason fan
var bs = E.buildStages(consistent);
ok('buildStages has >=5 stages', bs.stages.length >= 5);
var inclStage = bs.stages[bs.stages.length - 1];
eq('included stage label', inclStage.label, 'Studies included');
eq('included stage n', inclStage.n, 45);
ok('included stage has fan exits', Array.isArray(inclStage.exits) && inclStage.exits.length === 3);
eq('fan exit n preserved', inclStage.exits[0].n, 20);

// 14. zero-count excluded reasons are dropped from the fan
var withZero = E.buildStages(Object.assign({}, consistent, {
  excludedReasons: [{ reason: 'A', n: 20 }, { reason: 'B', n: 0 }, { reason: 'C', n: 25 }]
}));
var z = withZero.stages[withZero.stages.length - 1];
ok('zero-count reason dropped', z.exits.length === 2);

// 15. checklist is the full 27 items
eq('checklist length 27', E.CHECKLIST.length, 27);
ok('checklist item 1 is title', E.CHECKLIST[0].section === 'Title' && E.CHECKLIST[0].item === '1');
ok('checklist item 27 last', E.CHECKLIST[26].item === '27');

// 16. num() keeps 0, rejects blanks (?? not || semantics)
eq('num(0) is 0', E.num(0), 0);
eq('num("") is null', E.num(''), null);
eq('num(null) is null', E.num(null), null);

// 17. intEq tolerance
ok('intEq within tol', E.intEq(45, 45.0000001, 1e-3));
ok('intEq outside tol', !E.intEq(45, 46, 0.5));

console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail === 0 ? 0 : 1);
