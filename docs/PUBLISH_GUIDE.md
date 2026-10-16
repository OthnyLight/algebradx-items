# Publish guide: AlgebraDx item bank v1.0.0

Verification: confirmed by the author on 2026-10-10 (`docs/VERIFY_CHECKLIST.md`). The release build is unstamped, and the publish gate reports 0 blockers.

What you have:
- **`algebradx-items-v1.0.0.zip`**: the public release. It is already a git repository with one commit and the tag `v1.0.0`, so you only need to push it.
- **`algebradx-submission-kit.zip`**: private. It holds the MTLT article and the NCTM session kit. Keep it out of the public repository until each piece is accepted, because journals review blind and expect the manuscript not to be posted elsewhere.

Nothing was pushed or submitted from the build session. No GitHub or Zenodo token was supplied, and journal and conference submissions require your personal attestation.

Order: **GitHub → Zenodo (DOI) → DOI into files → MTLT article → NCTM proposal → log.** Allow about 75 minutes in total.

## 1. GitHub (10 min)
1. Go to github.com/new. Name: `algebradx-items`. Description: *Open diagnostic item bank for algebra readiness (grades 9–12): every wrong answer coded to a misconception.* Public. Leave it empty (no README, license or .gitignore).
2. **Before pushing the tag, do step 2.1** (switch Zenodo on for this repository) so the release mints a DOI automatically.
3. Unzip `algebradx-items-v1.0.0.zip`, open a terminal in the `algebradx-items` folder, and run:
   ```
   git remote add origin https://github.com/YOUR-USERNAME/algebradx-items.git
   git push -u origin main
   git push origin v1.0.0
   ```
4. On GitHub, go to Releases → Draft a new release → choose the existing tag `v1.0.0`. Title: "AlgebraDx Item Bank v1.0.0". Paste the v1.0.0 section of `CHANGELOG.md` as the notes, then publish.

## 2. Zenodo (10 min)
1. Log in at zenodo.org with ORCID 0009-0002-6113-6158. Go to Account → GitHub, click Sync, and switch on `algebradx-items` **before** step 1.4.
2. After the release, Zenodo creates a record within minutes. Edit it using `docs/zenodo_metadata.json`:
   - Upload type: **Dataset**
   - Title: *AlgebraDx Open Diagnostic Item Bank for Algebra Readiness (Grades 9–12)*
   - Creator: Sa'anga, Othniel Iyassa · ORCID 0009-0002-6113-6158 · Independent Researcher, Indianapolis, IN, USA
   - Description: from `zenodo_metadata.json`, which already includes the AI-assistance sentence
   - License: **CC BY 4.0** · Keywords: as in the file · Version: 1.0.0
   - Related identifier: your GitHub repository URL (*is supplemented by*)
3. Publish. Copy the **version DOI** and the **concept DOI** (the concept DOI stays the same across versions).

## 3. Put the DOI everywhere (10 min)
1. In `CITATION.cff`, add two lines under `license:`:
   ```
   doi: "10.5281/zenodo.NNNNNNN"
   repository-code: "https://github.com/YOUR-USERNAME/algebradx-items"
   ```
2. In `README.md`, replace "DOI: added after the Zenodo deposit." with the DOI link, and add the Zenodo badge from the record page.
3. Run `./run_all.sh --final`, then `git commit -am "Add DOI"` and `git push`. The article reads the DOI from `CITATION.cff`, so rebuild it as well (`node code/05_article.js --final` in the submission kit, after copying the updated `CITATION.cff` into it).

## 4. MTLT practitioner article (20 min)
- Venue: *Mathematics Teacher: Learning and Teaching PK–12* (NCTM), **Focus article**, 1,000–1,500 words including references (the current draft is 1,358), grade band 9–12. Submit at mc04.manuscriptcentral.com/mtltpk12.
- Check the current guidelines on nctm.org/write-for-mtlt first, especially anonymization. If a blinded file is required, make a copy with your name, affiliation, email and the DOI link removed ("link removed for review").
- Upload `practitioner_article.docx` and disclose AI assistance where the form asks, using the sentence in the article.
- Cover note: *This Focus article introduces a free, CC BY-licensed diagnostic item bank for grades 9–12 in which every wrong answer is coded to a research-documented misconception with a teaching move. The resource is deposited at https://doi.org/YOUR-DOI. The article has not been submitted elsewhere.*
- Save the manuscript ID to the evidence log.

## 5. NCTM session proposal (20 min)
- Open nctm.org/speak. Check, in order: the 2027 Orlando Annual (likely closed), the 2027 Seattle Spring Conference, the next Virtual Conference, then the 2028 Annual.
- Paste the title, description, objectives and abstract from `NCTM_session_kit.md`. Re-check the lengths against this call's limits. Speaker details must match your NCTM account.
- Save the proposal ID and notification date. Submit the same proposal to Indiana's state affiliate conference.

## 6. Log it the same day
Add one row per step to `docs/evidence_log.csv` (date, artifact, venue, URL or DOI, status, ID; the format is in the header). Save PDFs of the Zenodo record, the GitHub release page and each submission confirmation.
