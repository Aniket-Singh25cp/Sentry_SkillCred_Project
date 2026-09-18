# GB-200 Industrial Gearbox Service Manual, Rev B

**Document Number:** MAN-GB200-SVC-B  
**Revision:** Rev B  
**Issue Date:** 2023-11-20  
**Supersedes:** Rev A (2020-04-10)  
**Asset Class:** industrial_gearbox  
**Applicable Models:** GB-200, GB-210  
**Manufacturer:** Synthetix Fluid Systems Ltd.  
**Status:** Approved for Production Use

---

> **NOTICE:** This manual must be kept adjacent to the gearbox installation and be readily accessible to all maintenance personnel. Personnel must read all safety instructions in Section 1 before performing any task described herein.

---

## 1. Introduction and Safety Information

### 1.1 Document Purpose and Scope

This service manual covers the GB-200 and GB-210 series two-stage helical industrial gearbox manufactured by Synthetix Fluid Systems Ltd. The GB-200 is designed for continuous-duty power transmission in process plant applications including conveyor drives, mixer drives, and pump drives. Standard models accept input shaft speeds up to 1 500 RPM and are rated for gear ratio 4.2:1 (GB-200) or 6.5:1 (GB-210).

This manual covers receiving, installation, commissioning, preventive maintenance, and troubleshooting. For internal gear inspection, bearing clearance adjustment, or shaft seal replacement beyond the scope of Section 5, contact the Synthetix Regional Service Centre. Attempting internal gear disassembly without factory training may result in incorrect gear mesh, which cannot be detected without specialist measurement equipment and will reduce gearbox life severely.

### 1.2 Safety Signal Words

This manual uses safety signal words in accordance with ANSI Z535 and ISO 3864-2:

| Signal Word | Meaning |
|---|---|
| **DANGER** | Imminently hazardous situation which, if not avoided, **will result in death or serious injury.** |
| **WARNING** | Potentially hazardous situation which, if not avoided, **could result in death or serious injury.** |
| **CAUTION** | Potentially hazardous situation which, if not avoided, **may result in minor or moderate injury** or equipment damage. |
| **NOTICE** | Information important for correct operation. Not hazard-related. |

> **DANGER:** The gearbox operates at high torque with rotating shafts and exposed couplings. Entanglement with an unguarded rotating shaft is immediately fatal. Shaft guards must be in place and all LOTO applied before any access to the gearbox or its shaft connections.

> **WARNING:** The gearbox lubricating oil operates at up to 90 °C during normal duty. Allow at least 45 minutes after shut-down before opening the oil inspection cover or drain plug to avoid scalding. Wear heat-resistant gloves and eye protection.

> **CAUTION:** The gearbox housing is cast iron. Do not use impact wrenches on housing bolts. Impact loading may crack the housing, causing oil leakage and structural failure of the mounting.

### 1.3 Intended Use and Limitations

The GB-200 is approved for use with mineral gear oils ISO VG 150 to ISO VG 220 (per DIN 51517 Part 3, CLP designation). It is not suitable for: synthetic PAO oils without factory approval, foodgrade applications without the NSF H1 approved variant, environments with ambient temperature below −10 °C without a low-temperature oil kit, or shaft input powers exceeding the nameplate rating.

---

## 2. Technical Specifications

### 2.1 Gearbox Rating Data

| Parameter | Value | Unit |
|---|---|---|
| Model (standard) | GB-200 | — |
| Input shaft speed (rated) | 1 475 | RPM |
| Output shaft speed (rated) | 351 | RPM |
| Gear ratio | 4.2:1 | — |
| Rated input power | 22 | kW |
| Rated input torque | 142 | Nm |
| Maximum output torque | 580 | Nm |
| Service factor (SF) | 1.5 | — |
| Peak torque limit (before trip) | 870 | Nm |
| Oil fill capacity | 3.2 | litres |
| Rated oil temperature (outlet) | ≤ 90 | °C |
| Maximum ambient temperature | 40 | °C |
| Minimum ambient temperature | −10 | °C |
| Vibration limit (overall RMS) | 3.5 | mm/s |
| Noise level at 1 m (rated speed) | ≤ 72 | dB(A) |

### 2.2 Torque and Fastener Specifications

> **CAUTION:** Never use anti-seize compounds on internally-threaded housing bores unless specified. Anti-seize reduces the effective friction coefficient; the resulting bolt elongation may be insufficient to maintain clamp force.

| Location | Fastener | Torque (Nm) | Notes |
|---|---|---|---|
| Gearbox foot mounting bolts | M20 × 4 off | 280–300 | Grade 8.8; dry |
| Gearbox foot mounting bolts | M16 × 4 off (light frame) | 140–150 | Grade 8.8; dry |
| Input shaft coupling hub | M16 × 4 off | 120–130 | Lightly oiled |
| Output shaft coupling hub | M20 × 4 off | 200–220 | Lightly oiled |
| Top inspection cover bolts | M10 × 8 off | 35–40 | Lightly oiled |
| Oil drain plug (1" BSP) | — | 50–60 | PTFE tape |
| Oil filler/breather plug (3/4" BSP) | — | 30–35 | PTFE tape |
| Shaft seal retaining ring | M6 × 6 off | 10–12 | Loctite 243 |
| Oil temperature sensor (1/2" NPT) | — | 25–30 | PTFE tape |

---

## 3. Installation

### 3.1 Receiving and Inspection

Upon delivery, perform the following inspection before accepting the delivery:

**Procedure 3.1-A — Receiving Inspection:**

1. Check the gearbox nameplate against the purchase order: model, ratio, input speed, and rated power.
2. Rotate the input shaft by hand. Rotation should be smooth with no grinding or clicking. If rotation is stiff or impossible, the gearbox has been damaged in transit; do not install.
3. Inspect all shaft journals, keyways, and coupling mounting faces for nicks, rust, or burrs. Dress minor surface defects with a fine-cut file before fitting couplings.
4. Check that the factory oil fill (ISO VG 150 mineral gear oil, 3.2 litres) is present. The oil level should be visible at the mid-point of the site glass. If the unit was shipped dry, fill before commissioning (Section 5.2).
5. Inspect painted surfaces and all sealing faces for damage. Minor paint damage must be touched up before installation to prevent corrosion in service.
6. Record the gearbox serial number in the asset register and create a PM record.

### 3.2 Mounting and Alignment

The GB-200 must be mounted on a rigid, flat surface. The maximum allowable mounting distortion (soft-foot) is 0.05 mm, measured by inserting feeler gauges under each foot after tightening to full torque.

> **WARNING:** A gearbox mounted with excessive soft-foot will develop a housing distortion stress that propagates to the bearing races, causing premature bearing fatigue. Measure and correct soft-foot before initial commissioning and after any foot bolt re-tightening.

**Procedure 3.2-A — Mounting:**

1. Place the gearbox on the prepared foundation or frame. Hand-tighten the four foot bolts.
2. Check levelness of the input shaft axis in both horizontal planes using a precision level (tolerance: ≤ 0.5 mm/m). Adjust with stainless-steel shims under the feet.
3. Measure soft-foot: tighten all foot bolts to full torque (280–300 Nm for M20) and check for any gap under each foot with feeler gauges. If any foot shows a gap > 0.05 mm, the mounting surface is not flat; correct by machining the frame or by shimming the affected foot.
4. After all four feet are in contact and bolted, verify levelness has not changed during torquing.
5. Mark the foot bolt positions with a witness mark (paint line) so any subsequent movement can be detected.

### 3.3 Coupling Installation

> **WARNING:** Never drive a coupling hub onto a shaft using a hammer. Impact loading transfers force through the shaft into the bearing raceways (brinelling), causing immediate bearing damage. Use a purpose-made hub press or a hydraulic fitting tool only.

**Procedure 3.3-A — Coupling Hub Fitting:**

1. Clean the shaft journal and coupling hub bore with isopropyl alcohol. Remove any protective coating.
2. Inspect the shaft keyway for burrs; dress with a fine file.
3. Heat the coupling hub to 80–100 °C in a bearing oven (do not use a torch — uneven heating warps the hub). Slide the hub onto the shaft quickly while it is at temperature.
4. Fit the key and tighten the coupling hub retaining bolt to the torque specified in Section 2.2.
5. Allow to cool to ambient temperature before aligning (thermal contraction may affect readings).

---

## 4. Operation

### 4.1 Pre-Start Checklist

Before every start (including after maintenance), verify all of the following:

| Item | Requirement |
|---|---|
| Input and output shaft guards | Fitted and secured |
| Oil level (site glass) | Mid-level ±5 mm |
| Oil temperature | Within 5 °C of ambient (cold start confirmation) |
| Coupling condition | No visible cracks or missing rubber elements |
| Foot bolts | Witness marks aligned (no movement since last check) |
| Mounting bolts on driven equipment | Checked |
| Vibration baseline | Previous alarms cleared |

### 4.2 Break-In Period

New gearboxes and gearboxes after internal maintenance must undergo a break-in period to allow gear tooth surface and bearing raceway micro-asperities to bedding-in correctly.

**Procedure 4.2-A — Break-In:**

1. Start the gearbox unloaded (or at 25% of rated load) for 4 hours. Monitor oil temperature, vibration, and bearing housing temperature.
2. Drain the oil after the first 4-hour break-in. The drained oil will contain metallic fines from the gear surface contact; this is normal during break-in.
3. Flush the housing with 0.5 litre of clean ISO VG 150 oil; drain immediately.
4. Refill with fresh ISO VG 150 oil to mid-level.
5. Run at 50% rated load for 8 hours. Again monitor temperatures and vibration.
6. Drain and refill the oil one final time.
7. The gearbox may now be run at full rated load. Record the completion of break-in in the maintenance records.

> **NOTICE:** Failure to perform the break-in oil changes allows metallic fines from gear lapping to circulate in the oil, accelerating abrasive wear on the gear flanks and bearing raceways during the critical early period.

---

## 5. Maintenance

### 5.1 Preventive Maintenance Schedule

| Interval | Task | Reference |
|---|---|---|
| Daily | Visual inspection: leaks, coupling guard intact, bearing temperature check | — |
| Weekly | Oil sight glass level, foot bolt witness marks, ΔP across oil filter | 5.2 |
| Monthly | Vibration measurement (ODS or overall RMS at bearing housing) | — |
| 3-monthly | Oil change, inspect breather, inspect shaft seals | 5.2 |
| 6-monthly | Full alignment check, coupling insert inspection, oil sampling | 5.5 |
| Annually | Bearing inspection, internal gear inspection if vibration anomaly present | 5.4 |
| 3-yearly | Major overhaul including bearing replacement, gear mesh measurement | Synthetix Service Centre |

### 5.2 Oil Level Check and Drain

> **WARNING:** Allow the gearbox to cool for at least 45 minutes after shutdown before draining the oil. Oil operating at 80–90 °C will cause severe scalding burns.

The gearbox oil must be changed every 3 months or 2 000 operating hours, whichever occurs first, under standard industrial conditions. Change intervals should be halved in environments with high ambient dust, humidity above 85% RH, or frequent thermal cycling.

**Procedure 5.2-A — Oil Change:**

1. Perform lockout/tagout on the drive motor per SOP-LOTO-01. Verify zero-energy state.
2. Allow the gearbox to cool to below 40 °C (approximately 45 minutes after shutdown at rated temperature).
3. Remove the drain plug (1" BSP). Collect all oil in a clearly labelled drain container. Allow 10 minutes for complete drainage.
4. Inspect the drained oil visually:
   - Metallic particulate or grey sludge: indicates gear or bearing wear. Quantify by filtering a 100 ml sample through a 25-micron laboratory filter. Mass > 5 mg/100 ml requires inspection of the gear mesh and bearings.
   - Milky or grey-brown emulsion: water contamination. Investigate the source (shaft seal, condensation via breather, external water ingress). Clean the housing interior with flushing oil before refilling.
   - Black colour: oxidation/overheating. Check oil outlet temperature thermocouple calibration and operating conditions.
5. Replace the drain plug with fresh PTFE tape. Torque to 50–60 Nm.
6. Fill via the filler/breather port with fresh ISO VG 150 gear oil to the mid-point of the site glass. Do not overfill.
7. Replace the filler plug. Torque to 30–35 Nm.
8. Record oil change date, oil brand, and batch number in the PM log.

### 5.3 Gear Mesh Inspection

Internal gear mesh inspection is performed through the top inspection cover. This inspection should be triggered by:
- Any vibration trend showing frequency components at the gear mesh frequency (input speed × number of teeth on the pinion).
- Oil samples showing metal particle counts above threshold.
- The gearbox running noisier than baseline.

> **DANGER:** The gear mesh inspection requires the inspection cover to be removed. The gearbox must be fully stopped and locked out before removing the cover. Never attempt to inspect through an open cover with the gearbox running. Gear tooth contact forces at the mesh can eject metal fragments at high velocity.

**Procedure 5.3-A — Gear Mesh Inspection:**

1. Perform lockout/tagout per SOP-LOTO-01. Verify zero-energy state at the drive motor.
2. Clean the area around the top inspection cover with a lint-free cloth to prevent debris ingress.
3. Remove the 8 × M10 inspection cover bolts (35–40 Nm). Lift the cover straight up; do not pry. Retain the gasket.
4. Using a torch and mirror (or inspection camera), examine the following on the first-stage helical gear pair:
   - Tooth flank surface: should be smooth, with a uniform contact patch across at least 70% of the tooth face width. Pitting, spalling, or scuffing requires replacement.
   - Tooth root: inspect for surface cracks perpendicular to the tooth. Any cracks require immediate shutdown and factory assessment.
   - Gear flanks: check for micropitting (a grey, frosted appearance on the tooth flank). Micropitting in isolation, without pitting, can be managed with an oil viscosity upgrade; consult Synthetix Applications Engineering.
5. Rotate the input shaft by hand to expose all teeth for inspection (gear ratio 4.2:1 means approximately 4.2 full rotations of the input shaft to cycle through all output teeth).
6. Inspect the second-stage gear pair by directing the torch through the cover opening.
7. Refit the gasket (replace if compressed or torn) and the inspection cover. Torque bolts to 35–40 Nm in a cross pattern.
8. Record inspection findings and any actions taken.

### 5.4 Bearing Inspection

The GB-200 uses tapered roller bearings (Timken 32209J at the input shaft, Timken 32213J at the output shaft). Nominal service life is 35 000 hours L10 at rated load and 65 °C. Elevated temperature, misalignment, or oil contamination reduce life proportionally.

**Procedure 5.4-A — Bearing Condition Assessment:**

1. Perform lockout/tagout per SOP-LOTO-01.
2. Measure the bearing housing temperature with an infrared thermometer at four points around the housing circumference. Record all four readings. The maximum single-point temperature must not exceed 75 °C at steady state.
3. With the gearbox stationary, check bearing axial play by attempting to move the input shaft in the axial direction. Axial play above 0.25 mm (tapered roller bearings) indicates incorrect preload or bearing wear.
4. If vibration data is available, compare the spectrum against the characteristic bearing defect frequencies for the installed bearings. Consult Synthetix Technical Bulletin TB-GB200-03 for calculated BPFI/BPFO frequencies at rated speed.
5. Drain the oil and inspect the sump for metallic particles (see Section 5.2).
6. If bearing replacement is indicated, contact the Synthetix Regional Service Centre. Tapered roller bearing replacement requires specialist jigs and a preload measurement system; incorrect preload causes immediate bearing failure.

### 5.5 Shaft and Coupling Alignment Procedure

Shaft misalignment is the most common root cause of excessive vibration and premature bearing failure in the GB-200. Re-alignment is required after any foot bolt re-tightening, baseplate modification, or if vibration analysis shows a rising 1× or 2× running-speed component.

> **WARNING:** Perform lockout/tagout per SOP-LOTO-01 before mounting alignment instruments on the shaft or coupling. The drive motor must not be energised while personnel are working in the vicinity of the shafts.

**Procedure 5.5-A — Laser Shaft Alignment:**

1. Perform lockout/tagout on the drive motor.
2. Clean and inspect the coupling hubs. Replace worn rubber inserts before aligning.
3. Mount the laser transmitter/receiver pair on the input and output shaft coupling hubs per the alignment system manufacturer's instructions.
4. Record readings at 0°, 90°, 180°, and 270° rotation.
5. Acceptable alignment tolerances: radial (parallel) offset ≤ 0.05 mm TIR; angular misalignment ≤ 0.05 mm/100 mm.
6. Correct radial misalignment (vertical): shim the drive motor or driven machine feet as appropriate. Correct in the higher-deviation axis first.
7. Correct lateral (horizontal) misalignment: slide the machine on the slotted baseplate holes. Re-torque foot bolts and re-read after each correction.
8. When alignment is within tolerance, record final values, shim sizes, and any gap corrections in the maintenance log.
9. Reinstall all shaft guards.

---

## 6. Electrical Procedures

### 6.1 Lockout/Tagout Procedure

> **DANGER:** The drive motor connected to the GB-200 gearbox input shaft operates at voltages that are lethal on contact. All electrical isolation must be performed by an Authorised Person (AP) qualified for LV electrical work before any mechanical maintenance is begun.

The following LOTO procedure is mandatory before any work on the gearbox, its shaft connections, or associated seals and breathers.

**Procedure 6.1-A — Full Isolation and Lockout:**

1. Notify the control room operator and obtain a Permit to Work (PTW) from the Responsible Person (RP).
2. At the motor control centre (MCC), identify the feeder circuit breaker for the drive motor. Cross-check the circuit label against the work order and asset tag.
3. Turn the circuit breaker to the OFF position.
4. Apply personal safety lock(s) to the circuit breaker lockout hasp. Each technician working on the equipment must apply their own personal lock.
5. Test the motor terminals for absence of voltage using a calibrated voltage tester (IEC 61243 dual-function: live proving then dead testing). Measure phase-to-phase and phase-to-earth.
6. Attempt to start the motor from the local control panel and confirm it does not run.
7. Attach a danger tag: technician name, date, time, work order number, "DO NOT CLOSE."
8. Work may now commence on the gearbox.

> **WARNING:** If the drive motor is part of a variable-speed drive (VSD) system, the VSD capacitors may retain lethal charge for up to 5 minutes after power removal. Wait at least 5 minutes and measure the DC bus voltage at the VSD terminals (must be below 50 V DC) before opening any VSD enclosures or disconnecting motor leads.

**Re-energisation:**

1. Confirm all tools and personnel are clear.
2. Confirm all covers, guards, and fasteners are in place.
3. Each technician removes their personal lock.
4. The AP confirms the circuit is safe to re-energise and closes the circuit breaker.
5. Perform the pre-start checklist (Section 4.1) before starting.

---

## 7. Troubleshooting

### 7.1 Excessive Noise or Vibration

**Associated error codes:** G-101, G-102, G-103, G-114, G-115

**Symptom:** The gearbox is generating noise above baseline (subjectively louder, or SCADA vibration trending above 3.5 mm/s RMS), or vibration frequency analysis shows abnormal components.

**Diagnostic approach:**

| Noise/Vibration Character | Most Probable Cause | Primary Check |
|---|---|---|
| Steady whining at gear mesh frequency | Gear tooth profile error, overload | Section 5.3 gear inspection |
| Impulsive hammering / knocking | Worn or broken gear tooth | Section 5.3; shut down if progressive |
| Broad-spectrum rumbling, rising slowly | Bearing degradation | Section 5.4 |
| Dominant 1× and 2× running speed | Shaft misalignment | Section 5.5, 3.2 |
| Clicking or intermittent knock | Foreign object in gear mesh | Immediate shutdown; Section 5.3 |

**Detailed misalignment diagnosis (G-114, G-115):**

Shaft misalignment at the GB-200 input or output causes the following pattern:
- Overall vibration RMS above 3.5 mm/s.
- Dominant 1× (radial) and 2× (axial) components in the spectrum.
- Bearing temperatures slightly elevated (typically 5–12 °C above baseline) but within the warning band.
- Vibration typically appears abruptly after a maintenance event.

Confirm misalignment and correct per Section 5.5. After correction, re-run and verify overall vibration drops to below 2.0 mm/s.

> **WARNING:** Continued operation with misalignment above 0.15 mm TIR causes progressive coupling wear and accelerated bearing fatigue. Defer correction no more than 72 hours after diagnosis.

### 7.2 Oil Leakage

**Associated error codes:** G-205, G-206

**Symptom:** Oil observed on the gearbox housing, on the floor beneath the gearbox, or on adjacent equipment. Oil leakage is both an environmental hazard and a slip hazard.

**Diagnostic steps:**

1. Identify the source of the leak by cleaning the gearbox housing with a rag and observing where fresh oil appears after a 30-minute run.
2. Common leak locations and causes:
   - Input shaft seal: normal wear after > 20 000 hours, or accelerated by misalignment (shaft deflects and wears the seal lip).
   - Output shaft seal: same as above.
   - Inspection cover gasket: over-compressed or perished. Replace the gasket.
   - Drain plug: loose, damaged thread, or degraded PTFE tape. Re-torque or replace.
   - Filler/breather plug: blocked breather element causes internal pressure build-up, forcing oil past seals. Replace the breather element.
3. Quantify the leak rate. Drips from a shaft seal are acceptable up to 5 drops/hour during break-in; zero drops acceptable thereafter.
4. If the shaft seal is leaking, plan replacement at the next maintenance opportunity. Continued leakage will cause oil loss leading to under-lubrication.

### 7.3 Overheating

**Associated error codes:** G-107, G-108, G-109, G-110, G-113

**Symptom:** Oil temperature at the outlet thermocouple exceeds 90 °C, or the bearing housing temperature exceeds 75 °C.

**Causes and diagnostic steps:**

| Probable Cause | Diagnostic Check |
|---|---|
| Low oil level | Check site glass; fill if below mid-level |
| Incorrect oil grade (too thin) | Check oil grade against nameplate; drain and refill if wrong |
| Overloaded (torque above rating) | Compare measured current against rated; check driven machine load |
| Ambient temperature above 40 °C | Confirm ambient; add forced ventilation or oil cooler if needed |
| Oil cooler bypass open (G-113) | Check oil cooler bypass thermostatic valve (set to open at 85 °C) |
| Blocked oil filter | Check ΔP across oil filter; replace filter element if ΔP > 1.5 bar |

> **CAUTION:** Do not continue operating with oil temperature above 90 °C. Above this temperature, ISO VG 150 oil viscosity drops to a level insufficient to maintain hydrodynamic lubrication, causing metal-to-metal contact and severe gear wear within minutes.

### 7.4 Unusual Gear Wear

**Associated error codes:** G-201, G-202

**Symptom:** Oil samples show increasing metallic particle counts, or gear mesh inspection reveals pitting, scuffing, or micropitting on the tooth flanks.

**Diagnostic steps:**

1. Commission an oil analysis report from an accredited laboratory. Key results: particle count by ISO 4406 cleanliness code, iron content (ppm), copper content (ppm), and ferromagnetic debris (ferrogram).
2. Increase oil sampling frequency to monthly.
3. If pitting (spalling) is confirmed on gear flanks, shut down and contact the Synthetix Service Centre for a gear-set assessment. Continued operation with pitted teeth causes rapid material loss and eventual tooth fracture.
4. Micropitting without pitting can sometimes be arrested by increasing oil viscosity from ISO VG 150 to ISO VG 220. This requires factory approval; submit a deviation request via the Synthetix Field Service portal.

---

## 8. Error Code Reference Table

| Code | Meaning | Probable Causes | Cross-Reference |
|---|---|---|---|
| G-101 | Input shaft vibration high — warning | Bearing degradation (input), misalignment, gear mesh fault | Section 7.1, 5.4 |
| G-102 | Output shaft vibration high — warning | Bearing degradation (output), misalignment, driven machine fault | Section 7.1, 5.4 |
| G-103 | Gear mesh frequency abnormal | Gear tooth wear, incorrect mesh (after service), foreign object damage | Section 7.1, 5.3 |
| G-104 | Excessive backlash detected | Advanced gear flank wear, worn bearing causing shaft position shift | Section 5.3, 5.4 |
| G-105 | Input bearing temperature high — warning | Low oil, wrong oil grade, bearing wear, misalignment | Section 7.3, 5.4 |
| G-106 | Output bearing temperature high — warning | Same as G-105 for output bearing | Section 7.3 |
| G-107 | Oil temperature alarm | Low oil level, wrong oil grade, overload, blocked oil cooler | Section 7.3 |
| G-108 | Oil level low — warning | Oil leak from seal or drain plug, extended operation without top-up | Section 5.2, 7.2 |
| G-109 | Oil level low — alarm | Severe oil loss; imminent under-lubrication risk | Section 5.2 |
| G-110 | Oil pressure low | Blocked oil pump strainer, failed oil pump, low oil level | Section 5.2 |
| G-111 | Oil contamination sensor alarm | Water ingress, overheated oil oxidation, gear material contamination | Section 5.2 |
| G-112 | Oil filter differential pressure high | Clogged oil filter element (replace at ΔP > 1.5 bar) | Section 5.1 |
| G-113 | Oil cooler bypass valve open — alarm | Oil temperature too high; bypass opening prevents overcooling | Section 7.3 |
| G-114 | Input shaft misalignment detected | Coupling misalignment, soft-foot, thermal growth differential | Section 7.1, 5.5 |
| G-115 | Output shaft misalignment detected | Same as G-114 for output shaft | Section 7.1, 5.5 |
| G-201 | Gear tooth surface fatigue — pitting | Overload, inadequate lubrication, contact stress exceeding design | Section 7.4, 5.3 |
| G-202 | Micropitting detected (vibration analysis) | Insufficient lubricant film, oil viscosity too low for operating conditions | Section 7.4 |
| G-203 | Input coupling wear | Rubber insert degraded, coupling misaligned, overloaded | Section 3.3, 5.5 |
| G-204 | Output coupling wear | Same as G-203 for output coupling | Section 3.3 |
| G-205 | Shaft seal leak — input side | Seal lip worn, shaft surface worn, excessive misalignment | Section 7.2 |
| G-206 | Shaft seal leak — output side | Same as G-205 for output shaft | Section 7.2 |
| G-207 | Overload torque limit exceeded | Driven machine jam, sudden overload event, inertia transient | Section 7.3 |
| G-208 | Motor thermal protection trip | Sustained overload, high ambient, blocked motor fan | Section 6.1 |

---

## 9. Parts List and Ordering

Refer to Synthetix Parts Catalogue (PCat-GB200-B) for exploded drawings and part numbers.

| Part Description | Synthetix Part No. | Qty (12-month stock) |
|---|---|---|
| Input shaft bearing Timken 32209J | SFL-BRG-32209J | 2 |
| Output shaft bearing Timken 32213J | SFL-BRG-32213J | 2 |
| Input shaft seal (65×90×10, NBR) | SFL-SEAL-IS-GB200 | 2 |
| Output shaft seal (75×100×12, NBR) | SFL-SEAL-OS-GB200 | 2 |
| Inspection cover gasket | SFL-GSK-IC-GB200 | 4 |
| Oil filter element (25 µm) | SFL-FILT-OL-GB200 | 4 |
| Breather/vent element | SFL-BRTH-GB200 | 2 |
| Drain plug (1" BSP, stainless) | SFL-PLUG-DR-GB200 | 2 |
| Input coupling insert (polyurethane) | SFL-CUP-INS-GB200-IN | 2 |
| Output coupling insert (polyurethane) | SFL-CUP-INS-GB200-OUT | 2 |

---

## Revision History

| Revision | Date | Changes | Authorised By |
|---|---|---|---|
| Rev A | 2020-04-10 | Initial release | P. Andersson, Chief Engineer |
| Rev B | 2023-11-20 | Added G-114/G-115 alignment codes; updated LOTO procedure (Section 6.1) to align with ISO 45001:2018 and SOP-LOTO-01; added Section 5.5 alignment procedure; extended error code table to 24 codes; oil drain interval reduced from 6 months to 3 months | M. Okafor, Technical Author |

---

*End of GB-200 Industrial Gearbox Service Manual, Rev B*  
*Document Number: MAN-GB200-SVC-B | © 2023 Synthetix Fluid Systems Ltd. All rights reserved.*
