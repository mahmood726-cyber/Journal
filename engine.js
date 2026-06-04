/* PRISMA 2020 flow + checklist engine — pure, dependency-free, Node + browser.
 *
 * Deterministic arithmetic for the PRISMA 2020 study-selection flow and the
 * 27-item reporting checklist. The engine reconciles the user's reported counts
 * against the canonical identification -> screening -> included logic and
 * RETURNS warnings on any mismatch (it never throws), so a partially-entered or
 * internally-inconsistent flow still produces a usable diagram.
 *
 * Design notes / gotchas baked in (see README "Provenance"):
 *  - Numeric fallbacks use ?? (nullish), never || — || would drop a real 0
 *    (e.g. recordsOther = 0 is a valid "no other sources" entry).
 *  - Consistency checks compare expected vs given with an integer tolerance and
 *    report BOTH numbers so the user can see the discrepancy, not just that one
 *    exists.
 *  - The three identities follow PRISMA 2020 (Page et al., BMJ 2021):
 *      recordsScreened = recordsDb + recordsOther - duplicatesRemoved
 *      reportsAssessed = reportsSought - reportsNotRetrieved
 *      studiesIncluded = reportsAssessed - sum(excludedReasons.n)
 *  - excludedReasons is an itemised list [{reason, n}]; its sum feeds both the
 *    third identity and the multi-exit Sankey fan.
 */
(function (root) {
  'use strict';

  // integer-ish equality with a tolerance (counts are whole numbers but inputs
  // may arrive as floats from a number field); compares only when both defined.
  function intEq(a, b, tol) {
    tol = tol ?? 1e-6;
    return Math.abs(a - b) <= tol;
  }

  // coerce a value to a finite number or null (so missing fields stay missing
  // rather than silently becoming 0 — a 0 count is meaningful and distinct).
  function num(v) {
    if (v === null || v === undefined || v === '') return null;
    var n = typeof v === 'number' ? v : parseFloat(v);
    return isFinite(n) ? n : null;
  }

  // sum the n of an excludedReasons list; missing/blank n contributes 0.
  function sumExcluded(reasons) {
    if (!Array.isArray(reasons)) return 0;
    return reasons.reduce(function (acc, r) {
      var n = num(r && r.n);
      return acc + (n ?? 0);
    }, 0);
  }

  /* reconcile(input) -> { flow, derived, sumExcludedReasons, warnings }
   * input fields (all optional, numbers or null):
   *   recordsDb, recordsOther, duplicatesRemoved,
   *   recordsScreened, recordsExcluded,
   *   reportsSought, reportsNotRetrieved, reportsAssessed,
   *   excludedReasons: [{reason, n}],
   *   studiesIncluded, reportsIncluded
   *
   * Warnings are returned, never thrown. Each mismatch warning names the
   * expected value (from the identity) and the given value.
   */
  function reconcile(input) {
    input = input || {};
    var warnings = [];

    var recordsDb = num(input.recordsDb);
    var recordsOther = num(input.recordsOther);
    var duplicatesRemoved = num(input.duplicatesRemoved);
    var recordsScreened = num(input.recordsScreened);
    var recordsExcluded = num(input.recordsExcluded);
    var reportsSought = num(input.reportsSought);
    var reportsNotRetrieved = num(input.reportsNotRetrieved);
    var reportsAssessed = num(input.reportsAssessed);
    var studiesIncluded = num(input.studiesIncluded);
    var reportsIncluded = num(input.reportsIncluded);

    var sumExcl = sumExcluded(input.excludedReasons);

    // ---- identity 1: screened = db + other - duplicates --------------------
    // recordsOther defaults to 0 ("no other sources") via ?? so the identity
    // still resolves when only databases were searched.
    var derivedScreened = null;
    if (recordsDb !== null && duplicatesRemoved !== null) {
      derivedScreened = recordsDb + (recordsOther ?? 0) - duplicatesRemoved;
      if (recordsScreened !== null && !intEq(recordsScreened, derivedScreened, 0.5)) {
        warnings.push(
          'Records screened mismatch: given ' + recordsScreened +
          ', but recordsDb + recordsOther - duplicatesRemoved = ' + derivedScreened +
          ' (' + recordsDb + ' + ' + (recordsOther ?? 0) + ' - ' + duplicatesRemoved + ').'
        );
      }
    }

    // ---- identity 2: assessed = sought - notRetrieved ----------------------
    var derivedAssessed = null;
    if (reportsSought !== null && reportsNotRetrieved !== null) {
      derivedAssessed = reportsSought - reportsNotRetrieved;
      if (reportsAssessed !== null && !intEq(reportsAssessed, derivedAssessed, 0.5)) {
        warnings.push(
          'Reports assessed mismatch: given ' + reportsAssessed +
          ', but reportsSought - reportsNotRetrieved = ' + derivedAssessed +
          ' (' + reportsSought + ' - ' + reportsNotRetrieved + ').'
        );
      }
    }

    // ---- identity 3: included = assessed - sum(excludedReasons) -------------
    // use the given reportsAssessed when present, else the derived one.
    var derivedIncluded = null;
    var baseAssessed = reportsAssessed ?? derivedAssessed;
    if (baseAssessed !== null) {
      derivedIncluded = baseAssessed - sumExcl;
      if (studiesIncluded !== null && !intEq(studiesIncluded, derivedIncluded, 0.5)) {
        warnings.push(
          'Studies included mismatch: given ' + studiesIncluded +
          ', but reportsAssessed - sum(excludedReasons) = ' + derivedIncluded +
          ' (' + baseAssessed + ' - ' + sumExcl + ').'
        );
      }
    }

    // ---- sanity warnings (non-identity, still no throw) ---------------------
    if (recordsScreened !== null && recordsExcluded !== null &&
        reportsSought !== null &&
        !intEq(recordsExcluded + reportsSought, recordsScreened, 0.5)) {
      warnings.push(
        'Screening split mismatch: recordsExcluded + reportsSought = ' +
        (recordsExcluded + reportsSought) + ', but records screened = ' + recordsScreened + '.'
      );
    }

    var flow = {
      recordsDb: recordsDb,
      recordsOther: recordsOther,
      duplicatesRemoved: duplicatesRemoved,
      recordsScreened: recordsScreened,
      recordsExcluded: recordsExcluded,
      reportsSought: reportsSought,
      reportsNotRetrieved: reportsNotRetrieved,
      reportsAssessed: reportsAssessed,
      studiesIncluded: studiesIncluded,
      reportsIncluded: reportsIncluded
    };

    var derived = {
      recordsScreened: derivedScreened,
      reportsAssessed: derivedAssessed,
      studiesIncluded: derivedIncluded
    };

    return {
      flow: flow,
      derived: derived,
      sumExcludedReasons: sumExcl,
      warnings: warnings
    };
  }

  /* buildStages(input) -> stages array for ChartKit.renderSankey.
   * Each entry is { label, n, exits? }. Uses given values where present, falling
   * back to derived identities so the diagram is drawable from a partial flow.
   * The "Reports assessed -> Studies included" stage carries the itemised
   * exclusion-reason fan via exits:[{label, n}].
   */
  function buildStages(input) {
    var r = reconcile(input);
    var f = r.flow, d = r.derived;

    var identified = (f.recordsDb ?? 0) + (f.recordsOther ?? 0);
    var screened = f.recordsScreened ?? d.recordsScreened;
    var sought = f.reportsSought;
    var assessed = f.reportsAssessed ?? d.reportsAssessed;
    var included = f.studiesIncluded ?? d.studiesIncluded;

    var exits = (Array.isArray(input.excludedReasons) ? input.excludedReasons : [])
      .map(function (e) { return { label: String(e.reason ?? e.label ?? 'reason'), n: num(e.n) ?? 0 }; })
      .filter(function (e) { return e.n > 0; });

    var stages = [];
    stages.push({ label: 'Records identified', n: identified ?? 0 });
    if (screened !== null && screened !== undefined) {
      stages.push({
        label: 'Records screened', n: screened,
        exits: (f.duplicatesRemoved ?? 0) > 0
          ? [{ label: 'Duplicates removed', n: f.duplicatesRemoved }]
          : undefined
      });
    }
    if (sought !== null && sought !== undefined) {
      stages.push({
        label: 'Reports sought', n: sought,
        exits: (f.recordsExcluded ?? 0) > 0
          ? [{ label: 'Records excluded', n: f.recordsExcluded }]
          : undefined
      });
    }
    if (assessed !== null && assessed !== undefined) {
      stages.push({
        label: 'Reports assessed', n: assessed,
        exits: (f.reportsNotRetrieved ?? 0) > 0
          ? [{ label: 'Reports not retrieved', n: f.reportsNotRetrieved }]
          : undefined
      });
    }
    if (included !== null && included !== undefined) {
      stages.push({
        label: 'Studies included', n: included,
        exits: exits.length ? exits : undefined
      });
    }
    return { stages: stages, reconcile: r };
  }

  // ---- PRISMA 2020 27-item checklist (Page et al., BMJ 2021;372:n71) --------
  // Section / item# / topic text. Used by the UI to render the interactive list.
  var CHECKLIST = [
    { section: 'Title', item: '1', text: 'Identify the report as a systematic review.' },
    { section: 'Abstract', item: '2', text: 'See the PRISMA 2020 for Abstracts checklist.' },
    { section: 'Introduction', item: '3', text: 'Describe the rationale for the review in the context of existing knowledge.' },
    { section: 'Introduction', item: '4', text: 'Provide an explicit statement of the objective(s) or question(s) the review addresses.' },
    { section: 'Methods', item: '5', text: 'Specify the inclusion and exclusion criteria for the review and how studies were grouped for the syntheses.' },
    { section: 'Methods', item: '6', text: 'Specify all databases, registers, websites, organisations, reference lists and other sources searched or consulted, with the date each was last searched.' },
    { section: 'Methods', item: '7', text: 'Present the full search strategies for all databases, registers and websites, including any filters and limits used.' },
    { section: 'Methods', item: '8', text: 'Specify the methods used to decide whether a study met the inclusion criteria of the review, including how many reviewers screened each record and report.' },
    { section: 'Methods', item: '9', text: 'Specify the methods used to collect data from reports, including how many reviewers collected data from each report and any processes for obtaining or confirming data from study investigators.' },
    { section: 'Methods', item: '10', text: 'List and define all outcomes and all other variables for which data were sought, and any assumptions made about missing or unclear information.' },
    { section: 'Methods', item: '11', text: 'Specify the methods used to assess risk of bias in the included studies, including details of the tool(s) used and how many reviewers assessed each study.' },
    { section: 'Methods', item: '12', text: 'Specify for each outcome the effect measure(s) (e.g. risk ratio, mean difference) used in the synthesis or presentation of results.' },
    { section: 'Methods', item: '13', text: 'Describe the processes used to decide which studies were eligible for each synthesis, prepare the data, tabulate results, perform the synthesis, explore heterogeneity, assess sensitivity, and assess reporting biases (items 13a-13f).' },
    { section: 'Methods', item: '14', text: 'Describe any methods used to assess risk of bias due to missing results in a synthesis (arising from reporting biases).' },
    { section: 'Methods', item: '15', text: 'Describe any methods used to assess certainty (or confidence) in the body of evidence for an outcome.' },
    { section: 'Results', item: '16', text: 'Describe the results of the search and selection process, ideally using a flow diagram, and cite studies that met inclusion criteria but were excluded, with reasons (items 16a-16b).' },
    { section: 'Results', item: '17', text: 'Cite each included study and present its characteristics.' },
    { section: 'Results', item: '18', text: 'Present assessments of risk of bias for each included study.' },
    { section: 'Results', item: '19', text: 'For all outcomes, present, for each study, summary statistics for each group and an effect estimate with its precision (e.g. confidence/credible interval).' },
    { section: 'Results', item: '20', text: 'Present results of all syntheses, including summary estimates, heterogeneity, investigations of subgroups/sensitivity, and reporting biases (items 20a-20d).' },
    { section: 'Results', item: '21', text: 'Present assessments of risk of bias due to missing results (arising from reporting biases) for each synthesis assessed.' },
    { section: 'Results', item: '22', text: 'Present assessments of certainty (or confidence) in the body of evidence for each outcome assessed.' },
    { section: 'Discussion', item: '23', text: 'Provide a general interpretation of the results, limitations of the evidence and review processes, and implications for practice, policy and future research (items 23a-23d).' },
    { section: 'Other information', item: '24', text: 'Provide registration information, the protocol access location, and a description of any amendments (items 24a-24c).' },
    { section: 'Other information', item: '25', text: 'Describe and explain any amendments to information provided at registration or in the protocol; declare sources of financial or non-financial support and role of funders.' },
    { section: 'Other information', item: '26', text: 'Declare any competing interests of review authors.' },
    { section: 'Other information', item: '27', text: 'Report which of the following are publicly available and where: template data collection forms; data extracted; data used; analytic code; other materials.' }
  ];

  var api = {
    reconcile: reconcile,
    buildStages: buildStages,
    sumExcluded: sumExcluded,
    intEq: intEq,
    num: num,
    CHECKLIST: CHECKLIST
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.PrismaEngine = api;
})(typeof window !== 'undefined' ? window : this);
