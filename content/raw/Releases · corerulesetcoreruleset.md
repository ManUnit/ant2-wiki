---
title: "Releases · coreruleset/coreruleset"
source: "https://github.com/coreruleset/coreruleset/releases"
author:
  - "[[coreruleset]]"
published:
created: 2026-05-05
description: "OWASP CRS (Official Repository). Contribute to coreruleset/coreruleset development by creating an account on GitHub."
tags:
  - "clippings"
---
## What's Changed

### 🆕 New features and detections 🎉

- feat: Add WhatWAF to the scanner list by [@HackingRepo](https://github.com/HackingRepo) in [#4566](https://github.com/coreruleset/coreruleset/pull/4566)
- feat: Add ghauri to scanner list by [@HackingRepo](https://github.com/HackingRepo) in [#4570](https://github.com/coreruleset/coreruleset/pull/4570)
- feat: Expand Scanner User Agents List (v2) by [@HackingRepo](https://github.com/HackingRepo) in [#4572](https://github.com/coreruleset/coreruleset/pull/4572)
- feat: Expanded os files list by [@HackingRepo](https://github.com/HackingRepo) in [#4536](https://github.com/coreruleset/coreruleset/pull/4536)
- feat(933100): all HTTP headers should be checked by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4603](https://github.com/coreruleset/coreruleset/pull/4603)
- fix(lfi-os-files): add.dockerenv,.DS\_Store, META-INF/, WEB-INF/ by [@zoutjebot](https://github.com/zoutjebot) in [#4601](https://github.com/coreruleset/coreruleset/pull/4601)
- feat(934200): detect Server-Side Template Injection (SSTI) attacks by [@zoutjebot](https://github.com/zoutjebot) in [#4600](https://github.com/coreruleset/coreruleset/pull/4600)

### 🧰 Other Changes

- fix(lfi-os-files): require path prefix for.profile by [@zoutjebot](https://github.com/zoutjebot) in [#4586](https://github.com/coreruleset/coreruleset/pull/4586)
- fix(933150): remove is\_int from PHP function names list by [@zoutjebot](https://github.com/zoutjebot) in [#4585](https://github.com/coreruleset/coreruleset/pull/4585)
- fix(932370): remove url from Windows LOLBIN command list by [@zoutjebot](https://github.com/zoutjebot) in [#4587](https://github.com/coreruleset/coreruleset/pull/4587)
- fix(920539): prefer a bypass on a named rule rather than n+1 bypass by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4610](https://github.com/coreruleset/coreruleset/pull/4610)
- fix(942290): add word boundary to MongoDB operator detection by [@zoutjebot](https://github.com/zoutjebot) in [#4588](https://github.com/coreruleset/coreruleset/pull/4588)
- fix: false positive with parameter name `.history` by [@EsadCetiner](https://github.com/EsadCetiner) in [#4614](https://github.com/coreruleset/coreruleset/pull/4614)
- fix(942410): use common exceptions instead of rule by [@fzipi](https://github.com/fzipi) in [#4617](https://github.com/coreruleset/coreruleset/pull/4617)
- fix(942200): reduce false positives on payloads with comments by [@EsadCetiner](https://github.com/EsadCetiner) in [#4608](https://github.com/coreruleset/coreruleset/pull/4608)
- fix(unix): exclude `pg` command from pl-1 by [@EsadCetiner](https://github.com/EsadCetiner) in [#4613](https://github.com/coreruleset/coreruleset/pull/4613)
- fix(930130): comment out false positive prone entries by [@EsadCetiner](https://github.com/EsadCetiner) in [#4607](https://github.com/coreruleset/coreruleset/pull/4607)
- fix(920100): drop HTTP/0.9 GET support from request line validation by [@fzipi](https://github.com/fzipi) in [#4621](https://github.com/coreruleset/coreruleset/pull/4621)
- fix: Update restricted files to include Perl subdirectories by [@HackingRepo](https://github.com/HackingRepo) in [#4620](https://github.com/coreruleset/coreruleset/pull/4620)

## New Contributors

- [@zoutjebot](https://github.com/zoutjebot) made their first contribution in [#4586](https://github.com/coreruleset/coreruleset/pull/4586)

**Full Changelog**: [v4.25.0...v4.26.0](https://github.com/coreruleset/coreruleset/compare/v4.25.0...v4.26.0)

[v4.25.0 (LTS)](https://github.com/coreruleset/coreruleset/releases/tag/v4.25.0)

## What's Changed

### Important ⭐

These below fix [CVE-2026-33691](https://github.com/coreruleset/coreruleset/security/advisories/GHSA-rw5f-9w43-gv2w):

- fix(933111): prevent whitespace padding bypass in PHP double-extension upload by [@fzipi](https://github.com/fzipi) in [#4547](https://github.com/coreruleset/coreruleset/pull/4547)
- fix(933110): prevent whitespace padding bypass in PHP upload detection by [@fzipi](https://github.com/fzipi) in [#4546](https://github.com/coreruleset/coreruleset/pull/4546)
- fix(944140): prevent whitespace padding bypass in JSP file upload detection by [@fzipi](https://github.com/fzipi) in [#4548](https://github.com/coreruleset/coreruleset/pull/4548)

### 🆕 New features and detections 🎉

- feat(930130,930140): expand AI-based paths by [@Elnadrion](https://github.com/Elnadrion) in [#4540](https://github.com/coreruleset/coreruleset/pull/4540)
- feat: add aws security agent in scanners-user-agents.data by [@S0obi](https://github.com/S0obi) in [#4562](https://github.com/coreruleset/coreruleset/pull/4562)
- feat(932390): add shell fork bomb detection rule at PL2 by [@fzipi](https://github.com/fzipi) in [#4563](https://github.com/coreruleset/coreruleset/pull/4563)

### 🧰 Other Changes

- refactor: create 941250 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4520](https://github.com/coreruleset/coreruleset/pull/4520)
- refactor: create 942220.ra file by [@fzipi](https://github.com/fzipi) in [#4511](https://github.com/coreruleset/coreruleset/pull/4511)
- refactor: create rule 931100 and 931110 `.ra` files by [@Xhoenix](https://github.com/Xhoenix) in [#4489](https://github.com/coreruleset/coreruleset/pull/4489)
- feat: Adding critical ai dirs that previously not exist by [@HackingRepo](https://github.com/HackingRepo) in [#4535](https://github.com/coreruleset/coreruleset/pull/4535)
- refactor: create 933140 and 933180 `.ra` files by [@Xhoenix](https://github.com/Xhoenix) in [#4488](https://github.com/coreruleset/coreruleset/pull/4488)
- fix(944110,944120,944130,944150,944151,944200,944210,..): don't inspect cookies twice by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4526](https://github.com/coreruleset/coreruleset/pull/4526)
- refactor: create 943120 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4506](https://github.com/coreruleset/coreruleset/pull/4506)
- fix: false negative 932236 by [@franbuehler](https://github.com/franbuehler) in [#4544](https://github.com/coreruleset/coreruleset/pull/4544)
- feat: update list of unix commands by [@EsadCetiner](https://github.com/EsadCetiner) in [#4446](https://github.com/coreruleset/coreruleset/pull/4446)
- fix(932180): prevent whitespace padding bypass in restricted file upload detection by [@fzipi](https://github.com/fzipi) in [#4549](https://github.com/coreruleset/coreruleset/pull/4549)
- fix: harden GitHub Actions workflows by [@fzipi](https://github.com/fzipi) in [#4553](https://github.com/coreruleset/coreruleset/pull/4553)
- refactor: create 941310 `.ra` files by [@fzipi](https://github.com/fzipi) in [#4522](https://github.com/coreruleset/coreruleset/pull/4522)
- docs: update README by [@fzipi](https://github.com/fzipi) in [#4556](https://github.com/coreruleset/coreruleset/pull/4556)
- refactor: create 941120 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4498](https://github.com/coreruleset/coreruleset/pull/4498)
- fix(920540): allow rule exclusions for specific targets by [@EsadCetiner](https://github.com/EsadCetiner) in [#4405](https://github.com/coreruleset/coreruleset/pull/4405)
- fix(931130): ensure correct target is logged by [@EsadCetiner](https://github.com/EsadCetiner) in [#4577](https://github.com/coreruleset/coreruleset/pull/4577)

**Full Changelog**: [v4.24.1...v4.25.0](https://github.com/coreruleset/coreruleset/compare/v4.24.1...v4.25.0)

[v4.24.1](https://github.com/coreruleset/coreruleset/releases/tag/v4.24.1)

## What's Changed

### 🆕 New features and detections 🎉

- feat(930140): add AI coding assistant artifact protection by [@etiennemunnich](https://github.com/etiennemunnich) in [#4519](https://github.com/coreruleset/coreruleset/pull/4519)
- feat: Expand Scanner Agents by [@HackingRepo](https://github.com/HackingRepo) in [#4532](https://github.com/coreruleset/coreruleset/pull/4532)

### Fixes

- fix(942200): prevent matches against user agent strings by [@theseion](https://github.com/theseion) in [#4537](https://github.com/coreruleset/coreruleset/pull/4537)
- fix(942480): don't inspect cookies twice by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4524](https://github.com/coreruleset/coreruleset/pull/4524)

### 🧰 Other Changes

- refactor: create 934130 `.ra` file by [@Xhoenix](https://github.com/Xhoenix) in [#4487](https://github.com/coreruleset/coreruleset/pull/4487)
- refactor: create 941330 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4492](https://github.com/coreruleset/coreruleset/pull/4492)
- refactor: create 944300 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4490](https://github.com/coreruleset/coreruleset/pull/4490)
- refactor: create 941320 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4491](https://github.com/coreruleset/coreruleset/pull/4491)
- refactor: create 921160 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4497](https://github.com/coreruleset/coreruleset/pull/4497)
- refactor: create 921120 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4496](https://github.com/coreruleset/coreruleset/pull/4496)
- refactor: create 921110 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4495](https://github.com/coreruleset/coreruleset/pull/4495)
- feat: move 930110 to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4494](https://github.com/coreruleset/coreruleset/pull/4494)
- refactor: create 941190.ra file by [@fzipi](https://github.com/fzipi) in [#4499](https://github.com/coreruleset/coreruleset/pull/4499)
- refactor: create 941400 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4517](https://github.com/coreruleset/coreruleset/pull/4517)
- refactor: create 942250.ra file by [@fzipi](https://github.com/fzipi) in [#4512](https://github.com/coreruleset/coreruleset/pull/4512)
- refactor: create 941370 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4518](https://github.com/coreruleset/coreruleset/pull/4518)
- refactor: create 944260.ra file by [@fzipi](https://github.com/fzipi) in [#4510](https://github.com/coreruleset/coreruleset/pull/4510)
- feat: move 943100 to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4504](https://github.com/coreruleset/coreruleset/pull/4504)
- refactor: create 944120.ra file by [@fzipi](https://github.com/fzipi) in [#4508](https://github.com/coreruleset/coreruleset/pull/4508)
- refactor: create 942450.ra file by [@fzipi](https://github.com/fzipi) in [#4513](https://github.com/coreruleset/coreruleset/pull/4513)
- refactor: create 942510 and 942511.ra files with shared include by [@fzipi](https://github.com/fzipi) in [#4516](https://github.com/coreruleset/coreruleset/pull/4516)
- refactor: create 944240.ra file by [@fzipi](https://github.com/fzipi) in [#4509](https://github.com/coreruleset/coreruleset/pull/4509)
- docs: comment on threshold should be more alarming by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4330](https://github.com/coreruleset/coreruleset/pull/4330)
- chore: add missing regex-assembly comment blocks to rules by [@fzipi](https://github.com/fzipi) in [#4523](https://github.com/coreruleset/coreruleset/pull/4523)
- fix(913100): adding OWASP Nettacker to known scanners list by [@securestep9](https://github.com/securestep9) in [#4529](https://github.com/coreruleset/coreruleset/pull/4529)
- refactor: create 941300 `.ra` file by [@fzipi](https://github.com/fzipi) in [#4521](https://github.com/coreruleset/coreruleset/pull/4521)

## New Contributors

- [@etiennemunnich](https://github.com/etiennemunnich) made their first contribution in [#4519](https://github.com/coreruleset/coreruleset/pull/4519)
- [@securestep9](https://github.com/securestep9) made their first contribution in [#4529](https://github.com/coreruleset/coreruleset/pull/4529)
- [@HackingRepo](https://github.com/HackingRepo) made their first contribution in [#4532](https://github.com/coreruleset/coreruleset/pull/4532)

**Full Changelog**: [v4.24.0...v4.24.1](https://github.com/coreruleset/coreruleset/compare/v4.24.0...v4.24.1)

[v4.24.0](https://github.com/coreruleset/coreruleset/releases/tag/v4.24.0)

## What's Changed

### 🆕 New features and detections 🎉

- feat(933100): add detection of smarty template php tag by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4447](https://github.com/coreruleset/coreruleset/pull/4447)

### 🧰 Other Changes

- fix(932130): use lazy regex by [@fzipi](https://github.com/fzipi) in [#3730](https://github.com/coreruleset/coreruleset/pull/3730)
- chore(943110): move to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4431](https://github.com/coreruleset/coreruleset/pull/4431)
- fix(930130): reduce false positive by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4451](https://github.com/coreruleset/coreruleset/pull/4451)
- fix(920650): don't block on method override if it's not actually being overwritten by [@EsadCetiner](https://github.com/EsadCetiner) in [#4455](https://github.com/coreruleset/coreruleset/pull/4455)
- fix(932340): Add more UNIX FP commands by [@ssigwart](https://github.com/ssigwart) in [#4454](https://github.com/coreruleset/coreruleset/pull/4454)
- refactor(951210): convert maxDB leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4468](https://github.com/coreruleset/coreruleset/pull/4468)
- refactor(951190): convert Ingres leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4466](https://github.com/coreruleset/coreruleset/pull/4466)
- refactor(951140): convert EMC leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4464](https://github.com/coreruleset/coreruleset/pull/4464)
- refactor(951110): convert Access leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4463](https://github.com/coreruleset/coreruleset/pull/4463)
- fix: handle multi-byte UTF-8 chars in SQL special char detection by [@fzipi](https://github.com/fzipi) in [#4458](https://github.com/coreruleset/coreruleset/pull/4458)
- refactor(951200): convert Interbase leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4467](https://github.com/coreruleset/coreruleset/pull/4467)
- refactor(951180): convert Informix leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4465](https://github.com/coreruleset/coreruleset/pull/4465)
- refactor(951220): convert MSSQL leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4459](https://github.com/coreruleset/coreruleset/pull/4459)
- refactor(951250): convert SQLite leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4460](https://github.com/coreruleset/coreruleset/pull/4460)
- refactor(951260): convert Sybase leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4461](https://github.com/coreruleset/coreruleset/pull/4461)
- refactor(951130): convert DB2 leakage rule to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4462](https://github.com/coreruleset/coreruleset/pull/4462)
- fix: don't block json variable names called `profile` on libmodsecurity3/coraza by [@EsadCetiner](https://github.com/EsadCetiner) in [#4477](https://github.com/coreruleset/coreruleset/pull/4477)
- fix(933100): reduce false positive on Extensible Metadata Platform and xsl-stylesheets by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4445](https://github.com/coreruleset/coreruleset/pull/4445)
- feat: move 932190 to regex-assembly by [@theseion](https://github.com/theseion) in [#4475](https://github.com/coreruleset/coreruleset/pull/4475)
- fix(942200): FP against comma and single quote in French addresses by [@theseion](https://github.com/theseion) in [#4476](https://github.com/coreruleset/coreruleset/pull/4476)
- fix: add more exclusions for Google Funding Choices cookie by [@azurit](https://github.com/azurit) in [#4484](https://github.com/coreruleset/coreruleset/pull/4484)

**Full Changelog**: [v4.23.0...v4.24.0](https://github.com/coreruleset/coreruleset/compare/v4.23.0...v4.24.0)

[v4.23.0](https://github.com/coreruleset/coreruleset/releases/tag/v4.23.0)

## What's Changed

### ⭐ Important changes

- feat(920640): add rule to enforce content-type if there is body by [@fzipi](https://github.com/fzipi) in [#4406](https://github.com/coreruleset/coreruleset/pull/4406)

### 🆕 New features and detections 🎉

- feat(lfi): Add detection for Vite.js path traversal ([CVE-2025-30208](https://github.com/advisories/GHSA-x574-m823-4x7w "CVE-2025-30208")) by [@disisto](https://github.com/disisto) in [#4407](https://github.com/coreruleset/coreruleset/pull/4407)
- feat: block fake `mozilla/5.g` user-agent by [@EsadCetiner](https://github.com/EsadCetiner) in [#4383](https://github.com/coreruleset/coreruleset/pull/4383)
- feat: resolve common false positives with ad and tracker cookies by [@EsadCetiner](https://github.com/EsadCetiner) in [#4378](https://github.com/coreruleset/coreruleset/pull/4378)
- fix(ssrf): catch malformed urls by [@fzipi](https://github.com/fzipi) in [#4410](https://github.com/coreruleset/coreruleset/pull/4410)
- feat: block 'trap' command by [@azurit](https://github.com/azurit) in [#4422](https://github.com/coreruleset/coreruleset/pull/4422)
- feat: prevent php session files to be uploaded by [@fzipi](https://github.com/fzipi) in [#4412](https://github.com/coreruleset/coreruleset/pull/4412)
- feat(930130): improvement of the detection of common debug or error files across CMS platforms by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4426](https://github.com/coreruleset/coreruleset/pull/4426)
- feat(942450): add another hex + binary declaration pattern by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4374](https://github.com/coreruleset/coreruleset/pull/4374)
- feat: update restricted files and file extensions by [@EsadCetiner](https://github.com/EsadCetiner) in [#4299](https://github.com/coreruleset/coreruleset/pull/4299)
- feat(920650): add detection for framework method overrides by [@fzipi](https://github.com/fzipi) in [#4416](https://github.com/coreruleset/coreruleset/pull/4416)
- fix: remove Request-Range Header from rules by [@Xhoenix](https://github.com/Xhoenix) in [#4435](https://github.com/coreruleset/coreruleset/pull/4435)
- feat: block when Request-Range header is used by [@fzipi](https://github.com/fzipi) in [#4436](https://github.com/coreruleset/coreruleset/pull/4436)

### 🧰 Other Changes

- fix: remove bypass-vulnerable content types from default allow lists by [@RedXanadu](https://github.com/RedXanadu) in [#4365](https://github.com/coreruleset/coreruleset/pull/4365)
- feat(931131): removing off domain check by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4379](https://github.com/coreruleset/coreruleset/pull/4379)
- chore(933120): cleaning obsolete variable by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4417](https://github.com/coreruleset/coreruleset/pull/4417)
- chore(941360,941370,941380): cleaning useless capture keyword by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4419](https://github.com/coreruleset/coreruleset/pull/4419)
- chore(933151,933152,933153): cleaning useless variables by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4420](https://github.com/coreruleset/coreruleset/pull/4420)
- feat(942350): added replace keyword + c-type comment evasion by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4373](https://github.com/coreruleset/coreruleset/pull/4373)
- fix(933111): regex should be the same as 933110 by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4395](https://github.com/coreruleset/coreruleset/pull/4395)
- fix: FPs related to maxDB information leakage by [@azurit](https://github.com/azurit) in [#4382](https://github.com/coreruleset/coreruleset/pull/4382)
- fix: remove non-unix commands from unix rce rules (932230 PL-1, 932235 PL-1, 932250 PL-1, 932260 PL-1, 932220 PL-2, 932236 PL-2, 932239 PL-2, 932237 PL-3) by [@EsadCetiner](https://github.com/EsadCetiner) in [#4247](https://github.com/coreruleset/coreruleset/pull/4247)
- fix(941120): new regex is eligible for Paranoia Level 1 by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4291](https://github.com/coreruleset/coreruleset/pull/4291)
- fix(933150): reduce substring false positive matches by [@EsadCetiner](https://github.com/EsadCetiner) in [#4340](https://github.com/coreruleset/coreruleset/pull/4340)
- fix(942410): cleaning of duplicates with 942151 by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4336](https://github.com/coreruleset/coreruleset/pull/4336)
- fix: add separate rule to match unix commands with no arguments by [@EsadCetiner](https://github.com/EsadCetiner) in [#4273](https://github.com/coreruleset/coreruleset/pull/4273)
- fix(934140): update perl interpolation regex by [@fzipi](https://github.com/fzipi) in [#4250](https://github.com/coreruleset/coreruleset/pull/4250)
- feat(921200): move regexp to regex-assembly by [@fzipi](https://github.com/fzipi) in [#4409](https://github.com/coreruleset/coreruleset/pull/4409)
- fix(934190): add new rule to check localhost variants without scheme by [@fzipi](https://github.com/fzipi) in [#4429](https://github.com/coreruleset/coreruleset/pull/4429)
- feat(941110): all HTTP headers should be checked by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4326](https://github.com/coreruleset/coreruleset/pull/4326)
- feat(941120): all HTTP headers should be checked by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4327](https://github.com/coreruleset/coreruleset/pull/4327)

## New Contributors

- [@disisto](https://github.com/disisto) made their first contribution in [#4407](https://github.com/coreruleset/coreruleset/pull/4407)

**Full Changelog**: [v4.22.0...v4.23.0](https://github.com/coreruleset/coreruleset/compare/v4.22.0...v4.23.0)

[v3.3.8](https://github.com/coreruleset/coreruleset/releases/tag/v3.3.8)

## What's Changed

### ⭐ Important changes

### CRITICAL

- fix: 9AJ-260102 v3 by [@airween](https://github.com/airween) in [80d8047](https://github.com/coreruleset/coreruleset/commit/80d80473abf71bd49bf6d3c1ab221e3c74e4eb83)

## Fixes

- fix: move rule's phase 950100 to 3 by [@airween](https://github.com/airween) in [#3941](https://github.com/coreruleset/coreruleset/pull/3941)

Special thanks to [@daytriftnewgen](https://github.com/daytriftnewgen) for responsible reporting 9AJ-260102

**Full Changelog**: [v3.3.7...v3.3.8](https://github.com/coreruleset/coreruleset/compare/v3.3.7...v3.3.8)

[v4.22.0](https://github.com/coreruleset/coreruleset/releases/tag/v4.22.0)

## What's Changed

### CRITICAL

- fix for 9AJ-260102

### 🧰 Other Changes

- feat(934100): added sequence for [CVE-2025-55182](https://github.com/advisories/GHSA-fv66-9v8q-g76r "CVE-2025-55182") POCs by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4372](https://github.com/coreruleset/coreruleset/pull/4372)
- feat(942440): reduce false positive by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4346](https://github.com/coreruleset/coreruleset/pull/4346)
- fix(942431): reduce false positive with arrays in ARGS\_NAMES by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4305](https://github.com/coreruleset/coreruleset/pull/4305)
- fix: make regexen Rust's regex compatible by [@fgsch](https://github.com/fgsch) in [#4385](https://github.com/coreruleset/coreruleset/pull/4385)
- refactor: drop older spelling variants by [@fgsch](https://github.com/fgsch) in [#4386](https://github.com/coreruleset/coreruleset/pull/4386)

Special thanks to [@daytriftnewgen](https://github.com/daytriftnewgen) for responsible reporting 9AJ-260102

**Full Changelog**: [v4.21.0...v4.22.0](https://github.com/coreruleset/coreruleset/compare/v4.21.0...v4.22.0)

Dec 2, 2025

[fzipi](https://github.com/fzipi)[v4.21.0](https://github.com/coreruleset/coreruleset/tree/v4.21.0)

[`2ac6c00`](https://github.com/coreruleset/coreruleset/commit/2ac6c00a819411f538242fffabd4b5fa38614917)

[v4.21.0](https://github.com/coreruleset/coreruleset/releases/tag/v4.21.0)

## What's Changed

### 🆕 New features and detections 🎉

- feat(931100): add IPv6 support / XML scan and SSH scheme. by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4321](https://github.com/coreruleset/coreruleset/pull/4321)
- feat(920440): add new restricted file extensions by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4322](https://github.com/coreruleset/coreruleset/pull/4322)

### 🧰 Other Changes

- fix(942160): adding unit test for double comment by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4315](https://github.com/coreruleset/coreruleset/pull/4315)
- fix(920280, 920300, 920310, 920311, 920320, 920330): should be block by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4319](https://github.com/coreruleset/coreruleset/pull/4319)
- fix(942151,942152): wrong functions names by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4333](https://github.com/coreruleset/coreruleset/pull/4333)
- feat(942460): adding help for non-English folks by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4334](https://github.com/coreruleset/coreruleset/pull/4334)
- fix(932180): reduce substring false positives by [@EsadCetiner](https://github.com/EsadCetiner) in [#4338](https://github.com/coreruleset/coreruleset/pull/4338)
- fix(942151,942152): wrong functions names by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4337](https://github.com/coreruleset/coreruleset/pull/4337)
- fix(920180): wrong unit test - content-type evasion bypass by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4339](https://github.com/coreruleset/coreruleset/pull/4339)
- fix(956110): move rule to pl-2 by [@EsadCetiner](https://github.com/EsadCetiner) in [#4344](https://github.com/coreruleset/coreruleset/pull/4344)
- docs: comment on disabling `Expect` header in.Net by [@theseion](https://github.com/theseion) in [#4348](https://github.com/coreruleset/coreruleset/pull/4348)
- fix: add missing capture action to affected rules by [@airween](https://github.com/airween) in [#4361](https://github.com/coreruleset/coreruleset/pull/4361)

**Full Changelog**: [v4.20.0...v4.21.0](https://github.com/coreruleset/coreruleset/compare/v4.20.0...v4.21.0)

Nov 2, 2025

[fzipi](https://github.com/fzipi)[v4.20.0](https://github.com/coreruleset/coreruleset/tree/v4.20.0)

[`125990b`](https://github.com/coreruleset/coreruleset/commit/125990ba46b3747851cb2a51440b22b2a1bd13fc)

[v4.20.0](https://github.com/coreruleset/coreruleset/releases/tag/v4.20.0)

## What's Changed

### 🆕 New features and detections 🎉

- feat: update restricted file extensions by [@EsadCetiner](https://github.com/EsadCetiner) in [#4287](https://github.com/coreruleset/coreruleset/pull/4287)
- feat(930120): adding conf file for PrestaShop 1.6 / 1.7 / 8+ & Magento 2 by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4303](https://github.com/coreruleset/coreruleset/pull/4303)
- feat: add expect header to list of restricted headers by [@franbuehler](https://github.com/franbuehler) in [#4298](https://github.com/coreruleset/coreruleset/pull/4298)

### 🧰 Other Changes

- fix(942560): missing capture keyword by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4285](https://github.com/coreruleset/coreruleset/pull/4285)
- fix(932281): reduce false positive matches with json payload by [@EsadCetiner](https://github.com/EsadCetiner) in [#4288](https://github.com/coreruleset/coreruleset/pull/4288)
- fix(932240): reduce false positive matches with json payloads by [@EsadCetiner](https://github.com/EsadCetiner) in [#4290](https://github.com/coreruleset/coreruleset/pull/4290)
- fix(921180, 921210, 921220): should be block not pass by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4294](https://github.com/coreruleset/coreruleset/pull/4294)
- fix(942550): partial revert - too high risk of false positive by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4284](https://github.com/coreruleset/coreruleset/pull/4284)
- fix(942160): updating regex to deal with new payloads by [@touchweb-vincent](https://github.com/touchweb-vincent) in [#4292](https://github.com/coreruleset/coreruleset/pull/4292)

**Full Changelog**: [v4.19.0...v4.20.0](https://github.com/coreruleset/coreruleset/compare/v4.19.0...v4.20.0)