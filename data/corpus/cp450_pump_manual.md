# CP-450 Centrifugal Pump Service Manual, Rev C

**Document Number:** MAN-CP450-SVC-C  
**Revision:** Rev C  
**Issue Date:** 2024-03-15  
**Supersedes:** Rev B (2021-09-01)  
**Asset Class:** centrifugal_pump  
**Applicable Models:** CP-450, CP-460  
**Manufacturer:** Synthetix Fluid Systems Ltd.  
**Status:** Approved for Production Use

---

> **NOTICE:** This manual must be available to all personnel responsible for installing, operating, or maintaining the CP-450 series centrifugal pump. The manual must be kept in legible condition and stored near the equipment.

---

## 1. Introduction and Safety Information

### 1.1 Document Purpose and Scope

This service manual covers the CP-450 and CP-460 series single-stage, end-suction centrifugal pumps manufactured by Synthetix Fluid Systems Ltd. It provides guidance for installation, commissioning, routine operation, preventive maintenance, and troubleshooting. The procedures in this manual apply to standard configurations; consult the factory for custom impeller sizes, high-temperature fluid service above 120 °C, or hazardous-area (ATEX) variants.

The CP-450 is designed for continuous-duty pumping of clean, low-viscosity liquids including water, light hydrocarbons, and aqueous process solutions with a maximum solids concentration of 0.1 % by mass and particle size below 200 µm. Pumping of abrasive slurries, fluids with suspended fibre, or liquefied gases requires a modified impeller and seal package — contact Synthetix Applications Engineering before attempting such service.

### 1.2 Safety Signal Words

This manual uses the following signal words in accordance with ANSI Z535 and ISO 3864-2:

| Signal Word | Meaning |
|---|---|
| **DANGER** | Indicates an imminently hazardous situation which, if not avoided, **will result in death or serious injury**. |
| **WARNING** | Indicates a potentially hazardous situation which, if not avoided, **could result in death or serious injury**. |
| **CAUTION** | Indicates a potentially hazardous situation which, if not avoided, **may result in minor or moderate injury**, or damage to equipment. |
| **NOTICE** | Indicates information considered important for correct operation but not hazard-related. |

> **DANGER:** Never operate the pump against a closed discharge valve for more than 30 seconds. Recirculation heating will raise fluid temperature rapidly, resulting in flash vaporisation and potentially explosive release of pressurised vapour.

> **WARNING:** The CP-450 operates at shaft speeds up to 3 000 RPM. All rotating guards must be fitted and secured before starting the pump. Contact with unguarded rotating parts can cause severe laceration, degloving, or limb loss.

> **CAUTION:** Pumps in water service at ambient temperatures below 5 °C must be drained when not in service to prevent freeze damage to the casing, impeller, and mechanical seal.

> **NOTICE:** Synthetix Fluid Systems Ltd. accepts no liability for damage or injury resulting from operation outside the conditions stated on the pump nameplate or in this manual.

### 1.3 Intended Use and Limitations

The CP-450 is a decision-support tool for qualified maintenance technicians. It must not be used as the sole determinant for safety-critical actions; all procedures must be performed by personnel holding the relevant competency qualifications for mechanical and electrical work on rotating equipment.

**Operator qualification requirements:**
- Mechanical technician: NVQ Level 3 or equivalent in mechanical engineering maintenance, or demonstrated competency verified by a Responsible Person.
- Electrical technician: Authorised Person for LV systems per the Electricity at Work Regulations 1989 (or local equivalent).
- LOTO: All personnel performing maintenance on energised systems must hold a current Lockout/Tagout authorisation card, renewed annually.

---

## 2. Technical Specifications

### 2.1 Performance Data

| Parameter | Value | Unit |
|---|---|---|
| Rated flow (best efficiency point) | 185 | m³/h |
| Maximum continuous flow | 245 | m³/h |
| Minimum continuous flow | 80 | m³/h |
| Rated head | 52 | m |
| Maximum operating pressure (casing) | 16 | bar |
| Design pressure (hydrostatic test) | 24 | bar |
| Rated shaft speed (50 Hz) | 2 950 | RPM |
| Motor rated power | 37 | kW |
| Motor rated current (400 V, 3-phase) | 42 | A |
| Motor frame | IEC 225M | — |
| Suction nominal bore | DN 150 | — |
| Discharge nominal bore | DN 100 | — |
| Maximum fluid temperature | 120 | °C |
| Minimum fluid temperature | −10 | °C |
| Maximum fluid viscosity | 50 | cSt |
| Design temperature (mechanical seal) | 90 | °C |
| Maximum allowable working pressure (MAWP) | 12 | bar |
| Hydrostatic test pressure | 18 | bar |

### 2.2 Torque and Fastener Specifications

> **CAUTION:** Never use impact tools on bearing housing or seal gland fasteners. Impact loading may crack the cast-iron housing or damage the sealing face. Use calibrated torque wrenches only.

| Location | Fastener Size | Torque (Nm) | Lubrication |
|---|---|---|---|
| Suction flange (DN150, PN16) | M20 × 8 off | 90–100 | None (dry) |
| Discharge flange (DN100, PN16) | M16 × 8 off | 60–70 | None (dry) |
| Bearing housing to frame bolts | M16 × 4 off | 120–130 | Light oil |
| Bearing cover plate bolts | M10 × 6 off | 45–50 | Light oil |
| Impeller lock nut (LH thread) | M30 LH | 130–145 | Molykote® G-n Plus |
| Coupling half to shaft | M12 × 4 off | 55–60 | None (dry) |
| Motor foot bolts | M16 × 4 off | 120–130 | None (dry) |
| Seal gland plate screws | M8 × 4 off | 12–15 | None (dry) |
| Casing wear ring retaining screws | M6 × 6 off | 8–10 | Loctite 243 |
| Suction strainer flange bolts | M16 × 4 off | 60–70 | None (dry) |
| Drain plug (1/2" NPT) | — | 35–40 | PTFE tape |
| Oil filler/vent plug (3/8" BSP) | — | 20–25 | PTFE tape |

### 2.3 Fluid Compatibility

The standard CP-450 is compatible with clean water, cooling tower water, light fuel oil (ISO VG 32), and dilute aqueous acids/alkalis with pH 5–10. The mechanical seal is rated for continuous service up to 90 °C. For fluids outside these parameters, specify the appropriate seal material package (SiC/SiC, Hastelloy C, or PTFE bellows) at time of order.

---

## 3. Installation

### 3.1 Receiving and Inspection

Upon delivery, inspect the pump-motor set for transit damage before signing the delivery note. The following checks must be performed:

**Procedure 3.1-A — Receiving Inspection:**

1. Verify the pump nameplate data (model, serial number, rated head, flow, and pressure) against the purchase order.
2. Remove all transit covers from suction and discharge flanges. Inspect bore surfaces for damage, rust, or foreign material.
3. Rotate the shaft by hand (after removing the coupling guard). The shaft should turn freely with no grinding, clicking, or axial resistance. Stiff rotation indicates bearing damage in transit.
4. Check the oil level sight glass or dipstick on the bearing housing. The factory pre-fills the bearing housing with ISO VG 46 mineral oil to the centre of the sight glass. If the housing has been drained for freight, refill before commissioning (see Section 5.3).
5. Inspect all painted surfaces and machined joint faces for rust. Treat any rust spots with rust-inhibiting primer before installation.
6. Record the pump serial number, motor serial number, and date of receipt in the plant asset register.

> **NOTICE:** Synthetix Fluid Systems Ltd. will not accept warranty claims for damage attributable to improper storage, handling, or installation unless the receiving inspection record is available.

### 3.2 Foundation and Mounting

The CP-450 baseplate must be installed on a flat, rigid, vibration-damped concrete foundation or structural steel frame. Foundation sizing guidelines are given in the Installation Data Sheet (document IDS-CP450-C, supplied with each unit).

**Procedure 3.2-A — Baseplate Levelling:**

1. Clean the foundation surface and remove grout residue.
2. Place the baseplate on levelling shims (stainless steel, min. 100 mm from each corner).
3. Adjust shims until the baseplate is level in both axes to within 0.05 mm/m using a precision machinists' level.
4. Tighten anchor bolts to 120 Nm in a cross pattern.
5. Grout the void beneath the baseplate using non-shrink epoxy grout to a minimum depth of 25 mm. Allow to cure for the manufacturer's specified time (typically 72 h at 20 °C) before applying process loads.
6. Re-check levelness after grout cure and before coupling alignment.

### 3.3 Piping Connections

> **WARNING:** Piping must not impose forces or moments on the pump flanges that exceed the allowable nozzle loads stated in Table A3 of the pump data sheet. Excessive piping loads distort the casing, accelerate seal and bearing wear, and void the warranty.

Suction piping must be designed to minimise friction losses and ensure the fluid arrives at the impeller without cavitation. Follow these rules:

- The suction pipe diameter must be at least equal to the pump suction bore (DN150); a reducer must be eccentric, with the flat side uppermost, to avoid air pockets.
- Maintain a minimum straight-run length of five pipe diameters upstream of the suction flange.
- The suction strainer shall have a free area at least three times the pipe cross-section and shall include a differential pressure gauge connection across the element (see E-111 in Section 8).
- Install a fully-open isolation valve on the suction and discharge sides. Both valves must be rated for the system design pressure.
- Install a non-return (check) valve on the discharge side, between the pump and the discharge isolation valve, to prevent reverse flow on motor trip.

### 3.4 Initial Alignment Procedure

> **WARNING:** Do not connect the coupling halves or run the pump until shaft alignment has been verified with dial gauges or a laser alignment system. Misalignment above 0.15 mm TIR at operating temperature causes premature coupling and bearing failure and produces a characteristic vibration signature (see Section 7.2).

**Procedure 3.4-A — Shaft Alignment Check and Correction:**

1. Ensure both motor and pump are at operating temperature or apply a thermal growth correction factor from the pump data sheet.
2. Mount a dial gauge or laser prism fixture on the pump shaft, reading against the motor-shaft coupling half.
3. Rotate both shafts together through 360°. Record readings at 0°, 90°, 180°, and 270°.
4. Calculate radial offset (parallel misalignment) and angular misalignment from the readings.
5. Acceptable limits: radial offset ≤ 0.05 mm TIR; angular misalignment ≤ 0.05 mm/100 mm coupling length.
6. Correct by shimming the motor feet. Adjust in-plane (front/rear) misalignment with shims under the motor feet; correct lateral misalignment by shifting the motor on the slotted baseplate holes.
7. Re-tighten motor foot bolts to 120 Nm and repeat measurement. Iterate until alignment is within tolerance.
8. Install the coupling guard and secure all fasteners before proceeding.

---

## 4. Operation

### 4.1 Pre-Start Checklist

> **WARNING:** Never start the pump without confirming the pre-start checklist below. Starting dry, or with a closed suction valve, will destroy the mechanical seal within seconds and may cause overheating and ignition of flammable process fluids.

Before every start, confirm all of the following:

| Item | Requirement | Verified |
|---|---|---|
| Suction valve | Fully open | ☐ |
| Discharge valve | Throttled to ~25% open | ☐ |
| Oil level (sight glass) | Mid-level ± 5 mm | ☐ |
| Coupling guard | Fitted and secured | ☐ |
| Mechanical seal gland | No drips; flush supply on (if applicable) | ☐ |
| Pump casing | Primed and vented (see Section 4.3) | ☐ |
| Phase rotation | Correct (motor rotates CCW when viewed from drive end) | ☐ |
| Vibration baseline | Previous alarm limits cleared | ☐ |

### 4.2 Start-Up Procedure

**Procedure 4.2-A — Standard Start-Up:**

1. Confirm pre-start checklist (Section 4.1) is complete.
2. Energise the motor. The motor must reach rated speed within 8 seconds; if it does not reach 2 800 RPM within this period, trip the starter and investigate.
3. Immediately check suction pressure (should be ≥ 0.4 bar gauge). A suction pressure below 0.2 bar gauge indicates inadequate priming or a blocked suction strainer.
4. Slowly open the discharge valve over approximately 30 seconds until the desired flow rate is reached. Opening too rapidly causes water hammer.
5. Confirm discharge pressure is within the range 5.5–7.5 bar gauge at rated flow. Significant deviation indicates impeller wear, incorrect rotation, or a blocked impeller passage.
6. Check motor current against rated value (42 A). Current above 50 A indicates overload; current below 35 A at rated flow indicates cavitation or a partially blocked suction.
7. Observe the mechanical seal area. Occasional drips of clear fluid (up to 5 drops per minute) are acceptable for a packed gland; a cartridge mechanical seal should show zero leakage. Sustained leakage from a cartridge seal requires shut-down.
8. Record all readings in the shift log: time, suction pressure, discharge pressure, flow, current, bearing temperatures, and vibration (if permanently monitored).

### 4.3 Priming and Suction Requirements

The CP-450 is not self-priming. The casing and suction pipe must be filled with liquid before start-up. Priming methods vary by installation:

- **Flooded suction (preferred):** The liquid level is above the pump centreline. Open the suction valve slowly; liquid fills the casing by gravity. Open the vent plug on the casing top briefly to expel air.
- **Foot-valve priming:** A foot valve on the suction line retains liquid when the pump is stopped. Fill the casing via the priming port before start.
- **Vacuum priming:** An ejector or vacuum pump evacuates the casing and suction pipe. Ensure the system is airtight.

> **CAUTION:** If the pump is started unfilled (dry-run), the mechanical seal will fail within 10–30 seconds due to frictional heat. Any dry-run, even brief, requires seal inspection before returning the pump to service.

> **CAUTION:** The minimum net positive suction head available (NPSHa) must exceed the pump's NPSHr by at least 0.5 m at all operating conditions. Operating with insufficient NPSH will cause cavitation, which erodes the impeller and produces a characteristic erratic vibration and cracking/popping noise (error code E-102).

### 4.4 Normal Shutdown Procedure

**Procedure 4.4-A — Planned Shutdown:**

1. Slowly close the discharge valve over 20–30 seconds to prevent water hammer.
2. De-energise the motor at the motor control panel (MCP).
3. Close the suction isolation valve once the pump has fully stopped.
4. If the pump is to remain out of service for more than 72 hours, drain the casing via the drain plug to prevent stagnation and potential bacterial growth in the fluid.
5. Record the shutdown time and any abnormal observations in the shift log.

### 4.5 Emergency Shutdown

In an emergency (severe vibration, burning smell, visible fire, seal blow-out), perform an emergency stop as follows:

1. Press the EMERGENCY STOP button at the local panel.
2. Confirm motor contactor drops out (control panel indicator OFF).
3. Close both isolation valves only after confirming the pump has stopped.
4. Do not approach the pump until it has fully decelerated to rest.
5. Notify the supervisor and enter the event in the maintenance log.

> **DANGER:** After a seal blow-out on a flammable-liquid service pump, do not approach the pump until the area has been ventilated and confirmed gas-free by an authorised gas tester.

---

## 5. Maintenance

### 5.1 Preventive Maintenance Schedule

| Interval | Task | Reference Procedure |
|---|---|---|
| Daily | Check oil level, check for leakage, check bearing temperatures | 4.1 |
| Weekly | Inspect coupling for wear, check strainer differential pressure | 5.5 |
| Monthly | Grease coupling (if grease-lubricated type), check alignment TIR | 5.4 |
| 3-monthly | Change bearing lubricating oil, inspect seal, check motor current | 5.3, 5.6 |
| 6-monthly | Full vibration baseline measurement, inspect impeller clearance | — |
| Annually | Bearing inspection and replacement if needed, alignment verification | 5.2, 5.4 |
| 3-yearly | Major overhaul: impeller, wear rings, casing inspection | Workshop manual |

### 5.2 Bearing Inspection and Replacement

The CP-450 uses deep-groove ball bearings (SKF 6209-2RS at the drive end, SKF 6207-2RS at the non-drive end). Bearing life is design-rated at 40 000 hours L10 at rated load and 65 °C. Elevated temperature, misalignment, or oil contamination substantially reduce service life.

> **WARNING:** Apply lockout/tagout to the motor starter per SOP-LOTO-01 before removing the bearing housing cover. Failure to de-energize may result in unexpected shaft rotation and serious injury.

**Procedure 5.2-A — Bearing Inspection:**

1. Perform lockout/tagout on the motor circuit per SOP-LOTO-01. Verify zero-energy state by attempting to start from the local panel and confirming the motor does not run.
2. Remove the coupling guard. Disconnect and set aside the coupling insert (do not separate the coupling hubs unless hub inspection is required).
3. Drain the bearing housing oil via the drain plug. Collect the oil in a labelled container and retain for condition analysis if a bearing fault is suspected.
4. Remove the bearing cover plate (6 × M10 bolts, 45–50 Nm removal torque). Pull the cover plate straight off the shaft; do not pry.
5. Remove the bearing retaining circlip (where fitted). Heat the bearing outer race with a bearing heater set to 90 °C maximum; do not use an open flame.
6. Using a bearing puller, withdraw the bearing from the shaft journal. Do not apply force to the inner race unless the shaft journal is in good condition.
7. Inspect the removed bearing:
   - Rotate the inner race by hand. Smooth rotation with no grinding or sticking indicates a serviceable bearing. Grinding or high drag indicates contamination or spalling — replace.
   - Inspect the outer race raceway under strong light. Spalling (pitting or flaking of the raceway surface), brinelling (indentation marks), or discolouration indicating overheating all require replacement.
   - Inspect the shaft journal for fretting, grooves, or corrosion. A journal out of roundness by more than 0.015 mm requires re-grinding before fitting a new bearing.
8. Clean the housing bore and shaft journal with isopropyl alcohol and lint-free cloth.
9. If replacing the bearing: heat the new bearing to 80 °C ±10 °C in a bearing oven. Slide the bearing onto the shaft, press-fit until it seats against the locating shoulder. Do not hammer the bearing into position.
10. Refill the bearing housing with ISO VG 46 mineral oil to the centre of the sight glass (approximately 0.35 litres). Refit cover plate and torque bolts to 45–50 Nm.
11. Reconnect the coupling insert and refit the coupling guard.
12. Remove lockout devices only after all guards are refitted and personnel are clear.
13. Run the pump under load for 30 minutes; recheck bearing temperature with an infrared thermometer. Drive-end bearing temperature must not exceed 75 °C.

> **CAUTION:** Use only pre-approved bearing lubricating oil (ISO VG 46 mineral oil, or equivalent per Synthetix approval list SFL-OIL-001). Mixing oils of different viscosity grades or additive packages degrades lubrication performance and voids the warranty.

### 5.3 Lubrication and Oil Service

Bearing lubricating oil must be changed every three months or 2 000 operating hours, whichever occurs first. After any bearing fault, oil contamination event, or water ingress, change the oil immediately regardless of scheduled interval.

> **DANGER:** Isolate and lock out the motor circuit before opening the bearing housing or lubricant reservoir. Rotating components can cause entanglement even at slow speeds.

**Procedure 5.3-A — Oil Change:**

1. Perform lockout/tagout on the motor circuit per SOP-LOTO-01.
2. Allow the bearing housing to cool to below 40 °C if the pump has recently been running.
3. Place a suitable drain pan (minimum 1 litre capacity) beneath the bearing housing drain plug.
4. Remove the drain plug (1/2" NPT) and allow all oil to drain. Flush with 0.1 litre of clean ISO VG 46 oil and drain again if the drained oil shows cloudiness, dark sludge, or metallic particles.
5. Inspect the drained oil:
   - Milky or cream-coloured oil: water contamination. Investigate the source (shaft seal, external moisture, condensation).
   - Dark sludge or metallic particles: advanced bearing or gear wear. Submit a sample to an oil analysis laboratory before returning to service.
   - Normal condition: amber colour, slight oil smell, no visible particulate.
6. Refit the drain plug with fresh PTFE tape. Torque to 35–40 Nm.
7. Remove the oil filler/vent plug (3/8" BSP). Pour fresh ISO VG 46 oil (approximately 0.35 litres) until the oil level reaches the midpoint of the sight glass. Do not overfill (overfilling causes oil foaming and elevated operating temperature).
8. Replace the filler/vent plug. Torque to 20–25 Nm.
9. Remove lockout devices, restart the pump, and allow to run for 15 minutes. Recheck the oil level through the sight glass; top up if needed.
10. Record the oil change in the PM records, including oil brand, batch number, and oil level after topping up.

**Oil Level Alarm Thresholds:**

| Level | Sight Glass Appearance | Action |
|---|---|---|
| Normal | Midpoint of glass ±5 mm | No action |
| Warn low (40% of glass) | Oil level below 40 mm | Top up at next opportunity |
| Alarm low (25% of glass) | Oil level at or below 25 mm | Shut down and top up immediately (triggers E-204) |
| Overfull | Oil above top mark | Drain excess; foaming risk |

> **CAUTION:** An oil level at or below the alarm-low mark indicates insufficient lubricant film on the bearings. Continued operation beyond this point causes bearing failure within minutes at full load.

### 5.4 Shaft Alignment Procedure

Re-alignment is required after: any bearing replacement, motor or pump baseplate movement, piping configuration change, or if vibration measurements indicate a 1× or 2× running-speed component increasing over time.

> **WARNING:** De-energize and lock out the motor before mounting or dismounting the dial gauge fixture or laser targets on the coupling. Proximity to rotating equipment during energised operation is prohibited without specific risk assessment and written permit.

**Procedure 5.4-A — Laser Alignment (preferred):**

1. Perform lockout/tagout on the motor circuit per SOP-LOTO-01.
2. Allow the machine train to reach thermal equilibrium (or apply growth corrections from the data sheet).
3. Remove the coupling insert. Mount the laser transmitter/receiver heads on each shaft half per the alignment system manufacturer's instructions.
4. Rotate both shafts through 360° (in the direction of normal rotation) recording four readings at 90° intervals.
5. Enter the machine dimensions into the alignment software. Observe the graphical display showing parallel offset and angular misalignment in both horizontal and vertical planes.
6. Correct vertical misalignment first: adjust motor foot shims (0.05 mm increments). After each shim change, re-torque motor foot bolts to 120 Nm before re-reading.
7. Correct horizontal misalignment: slacken motor foot bolts and slide motor in the lateral direction using the baseplate adjustment slots. Re-torque and re-read.
8. Achieve ≤ 0.05 mm TIR parallel offset and ≤ 0.05 mm/100 mm angular misalignment in both planes.
9. Reinstall the coupling insert and coupling guard.
10. Record the final alignment values, shim thicknesses, and the alignment system serial number in the maintenance log.

### 5.5 Suction Strainer and Filter Service

The suction strainer (element mesh size 1.6 mm, stainless steel AISI 316) protects the impeller from solid debris. A differential pressure (ΔP) gauge or transmitter shall be installed across the strainer. A rising ΔP indicates element blinding and is the primary cause of error code E-111.

**Procedure 5.5-A — Strainer Cleaning:**

1. Shut down the pump per Section 4.4.
2. Close the suction isolation valve.
3. Depressurise the suction line via the vent valve upstream of the strainer.
4. Remove the strainer element access cover (4 × M16 bolts, 60–70 Nm removal torque). Retain the O-ring.
5. Withdraw the strainer basket. Flush with clean water or compressed air (max. 6 bar) from inside out to dislodge debris. Inspect for tears, cracks, or corrosion pitting in the mesh — replace the basket if any damage is found.
6. Inspect the strainer housing internally for scale or biological growth. Clean with a suitable descaler or biocide solution if required (ensure compatibility with the process fluid).
7. Replace the basket and O-ring. O-ring should be lightly lubricated with silicone grease before fitting. Refit the access cover and torque bolts to 60–70 Nm in a cross pattern.
8. Open the suction valve slowly and vent the suction pipe. Restart per Section 4.2.
9. Monitor ΔP across the strainer for the first 30 minutes. A rapid return to high ΔP indicates unusual debris loading; investigate the upstream source.

> **CAUTION:** Do not operate the pump with the strainer element removed. Debris ingestion will damage the impeller and wear rings within minutes.

### 5.6 Mechanical Seal Inspection

The standard CP-450 is fitted with a single cartridge mechanical seal (SFT-CS100 or approved equivalent). The seal requires no routine adjustment.

Inspect the seal area at every shift for drips. A cartridge mechanical seal must show zero leakage under all normal operating conditions. Any visible dripping from the seal gland area indicates seal face damage, seal face contamination, or loss of flush flow (where applicable) and requires planned shutdown for seal replacement.

> **CAUTION:** Never operate the pump with a leaking mechanical seal on a flammable or toxic fluid service. Seal failure can escalate to complete seal blow-out within hours.

---

## 6. Electrical Procedures

### 6.1 Lockout/Tagout for Motor Disconnect

> **DANGER:** De-energize and lock out the motor at the motor control centre (MCC) using an approved lockout device before removing the coupling guard or performing any work on rotating components.

All electrical work on the motor starter, termination box, or associated control circuits must be performed by an Authorised Person (AP) per the plant Electrical Safe Systems of Work (ESSOW) procedure. Mechanical technicians performing coupling, bearing, or seal work must confirm the motor is locked out before approaching the drive end.

**Procedure 6.1-A — Motor LOTO:**

1. Notify the control room operator that the pump is being isolated for maintenance. Obtain a permit to work (PTW) from the Responsible Person (RP).
2. At the motor control centre (MCC), identify the correct feeder circuit breaker for the pump motor. Verify identification by comparing the circuit label and asset tag against the maintenance work order.
3. Turn the circuit breaker to the OFF position.
4. Apply a personal safety lock to the circuit breaker lockout hasp. Record the lock number in the PTW document.
5. Where multiple technicians are working on the same equipment, each technician must apply their own personal lock (one person, one lock, one key).
6. Test the motor circuit for absence of voltage using a calibrated dual-function voltage tester (live-proving, dead-testing cycle per IEC 61243).
7. Attempt to start the pump from the local control panel (if accessible). Confirm the motor does not start.
8. Attach a danger tag to the circuit breaker stating: technician name, date, time, work order number, and the instruction "DO NOT CLOSE THIS ISOLATOR — PEOPLE AT RISK."
9. Work may now commence on the pump mechanical components.

> **WARNING:** Personal safety locks must remain in place until ALL personnel have completed their work and confirmed they are clear of the equipment. The last technician to leave must remove the group box lock (if used) only after all personal locks are removed.

**Re-energisation after maintenance:**

1. Confirm all tools, rags, and foreign objects have been removed from the pump and motor.
2. Confirm all guards are refitted and all fasteners are torqued.
3. All technicians remove their personal locks.
4. Close the MCC circuit breaker and confirm the control panel shows healthy status.
5. Perform the pre-start checklist (Section 4.1) before starting.

### 6.2 Motor Winding Inspection

Winding insulation resistance (IR) testing must be performed annually and after any moisture ingress or overtemperature event.

**Procedure 6.2-A — Insulation Resistance Test:**

1. Perform LOTO per Section 6.1-A.
2. Disconnect all motor terminal leads at the termination box. Identify and label each terminal (U1, V1, W1, U2, V2, W2 for delta/star changeover motors).
3. Using a calibrated megohmmeter set to 500 V DC, measure IR from each winding phase to earth and between phases. Allow the reading to stabilise for 60 seconds before recording.
4. Minimum acceptable IR at 20 °C: 100 MΩ (motor in service); 10 MΩ minimum for continued operation.
5. Apply the polarisation index (PI = IR at 10 min / IR at 1 min). A PI above 2.0 indicates healthy insulation. A PI below 1.5 indicates moisture absorption or degradation.
6. Record all values and compare with previous test. A steady decline in IR over successive tests, even while above the minimum threshold, indicates incipient failure.

### 6.3 Phase Balance Verification

Phase imbalance in the supply voltage causes unequal heating of the motor windings and accelerated insulation degradation. It may also reduce motor torque capacity, causing the pump to run below rated speed.

**Procedure 6.3-A — Phase Balance Check:**

1. With the motor running at rated load, measure the current in each phase (U, V, W) using a calibrated clamp meter.
2. Calculate the percentage phase current imbalance: `imbalance (%) = (max deviation from average / average) × 100`.
3. Acceptable limit: phase current imbalance ≤ 5 %. Values above 10 % trigger error code E-303 and require investigation of the supply voltage balance at the MCC.
4. Also measure voltage at the motor terminals. Voltage imbalance above 2 % can cause current imbalance of 6–10× the voltage imbalance. Investigate at the MCC distribution board if voltage imbalance exceeds 1 %.

> **CAUTION:** Phase imbalance above 10% will cause the motor to run hot on the high-current phase. Prolonged operation can cause insulation failure and motor winding burnout. Shut down and correct the supply if imbalance exceeds this limit.

---

## 7. Troubleshooting

Use the error code table (Section 8) as the first step when a fault code appears on the motor control panel or SCADA system. The subsections below provide supplementary diagnostic procedures for the most frequent fault types.

> **DANGER:** Before performing any physical inspection that requires opening the pump, removing guards, or working in the vicinity of rotating components, perform full lockout/tagout per Section 6.1. Never troubleshoot on a running machine unless explicitly stated (e.g., taking vibration readings from external measurement points with all guards in place).

### 7.1 Reduced Flow or Pressure

**Associated error codes:** E-104, E-109, E-102

**Symptom:** The pump is running (motor current normal or reduced), but flow or discharge pressure is below the expected operating point. The technician may observe low flow alarm on the process flow meter.

**Diagnostic procedure:**

1. Read suction pressure at the pump suction gauge (should be ≥ 0.4 bar gauge at rated conditions). If suction pressure is low (below 0.2 bar gauge or below the NPSHa threshold for this installation), proceed to Step 2. If suction pressure is normal, proceed to Step 5.
2. Check the suction isolation valve is fully open. A partially open valve throttles suction flow and reduces performance.
3. Check the suction strainer differential pressure (ΔP). A ΔP above 0.3 bar indicates a partially blocked strainer; service per Section 5.5.
4. Vent the pump casing. Air trapped in the casing reduces effective impeller area and causes erratic performance. Open the casing vent plug for 3–5 seconds. If a rush of air or vapour is observed, the pump has lost its prime; re-prime per Section 4.3.
5. Check motor current against rated value. If motor current is significantly below rated (below 35 A at expected operating point), impeller wear may be causing performance reduction. Measure discharge pressure against the pump performance curve at the operating speed.
6. If motor current is above rated (above 50 A), the pump is running in an overloaded condition, possibly at a flow point beyond the best efficiency point (BEP). Throttle the discharge valve slightly and recheck.
7. Inspect the discharge check valve. A failed-open check valve allows backflow through the pump when a parallel pump is running; this can cause one pump to appear to be producing zero net flow.

**Cavitation diagnosis:**

If the pump emits a cracking, popping, or rattling noise during the above investigation, and suction pressure is low, cavitation is the probable cause (error code E-102). Confirm by:
- Comparing suction pressure with the NPSHr from the pump curve at the operating flow.
- Examining the impeller suction face (requires pump disassembly) for erosion pitting or cratering.
- Checking for vapour in the suction line (flash from a hot fluid source, dissolved gas release, or vortex at an open sump).

**Remedial actions for cavitation:**

- Raise the liquid level in the suction vessel.
- Fully open the suction valve and remove any restrictions.
- Reduce the flow rate by partially closing the discharge valve.
- Cool the suction fluid if flash vaporisation is occurring.
- Increase the suction pipe diameter or reduce bends in the suction line.

### 7.2 Excessive Vibration — Misalignment

**Associated error codes:** E-105

**Symptom:** Vibration RMS levels above 4.5 mm/s at the bearing housings. Vibration frequency analysis (if available) shows dominant components at 1× running speed (radial) and 2× running speed (axial). Bearing temperatures may be mildly elevated (5–10 °C above baseline) but are typically within warning range, not alarm.

**Diagnostic procedure:**

1. Confirm that all coupling guard bolts are tightened. A loose guard can vibrate at running frequency and falsely elevate overall vibration levels.
2. Perform a trend check on vibration data. Misalignment-induced vibration typically appears abruptly after maintenance (coupling or bearing work) rather than developing gradually.
3. Remove the coupling guard and visually inspect the coupling insert for wear (crumbling rubber, crushed spider legs, or rubber debris at the coupling joint). Worn coupling elements can amplify misalignment-induced vibration.
4. Perform laser shaft alignment measurement per Section 5.4. Compare measured misalignment values with tolerances stated in Section 3.4.
5. If misalignment is confirmed above tolerance, correct per Section 5.4.
6. After correction, re-measure vibration with the pump running at rated flow. Vibration should reduce to below 2.8 mm/s at rated conditions for a well-aligned machine.

> **CAUTION:** Continued operation with misalignment above 0.15 mm TIR will cause accelerated coupling wear and bearing failure within weeks to months depending on the severity. Do not defer alignment correction beyond the next planned shutdown.

### 7.3 Excessive Vibration — Bearing Fault

**Associated error codes:** E-107 (drive end), E-108 (non-drive end)

**Symptom:** Vibration RMS levels rising progressively over weeks. Bearing temperature rising above 75 °C at the drive end or non-drive end. If frequency analysis is available, characteristic bearing defect frequencies (BPFI, BPFO, BSF, FTF) are visible in the spectrum. The combined presentation of rising vibration and rising bearing temperature is highly specific to bearing degradation.

**Diagnostic procedure:**

1. Download vibration trend data from the condition monitoring system. Confirm the progressive trend (distinguishes bearing fault from sudden misalignment).
2. Measure current bearing temperature with a calibrated infrared thermometer (aim at the bearing housing OD, not the shaft seal area, to avoid emissivity errors). Record drive-end (DE) and non-drive-end (NDE) temperatures.
3. Compare temperatures against baselines:
   - Normal: DE ≤ 65 °C, NDE ≤ 60 °C
   - Warning: DE 65–75 °C, NDE 60–72 °C
   - Alarm: DE > 75 °C, NDE > 72 °C (immediate action required)
4. Check the bearing housing oil level (Section 5.3). Low oil level accelerates bearing degradation and elevates temperature. If the oil level is at the alarm-low mark, add oil immediately and investigate the cause of oil loss.
5. If temperature is in the alarm band and vibration RMS exceeds 7 mm/s, schedule urgent bearing replacement (within 24 hours); if vibration exceeds 9 mm/s or temperature exceeds 85 °C, initiate immediate shut-down.
6. Perform bearing replacement per Section 5.2. Submit a sample of the drained oil for laboratory analysis.

> **WARNING:** A bearing in the alarm band may fail without further warning within hours. Do not leave the machine unattended once bearing temperature exceeds 80 °C. Station a technician to monitor temperature at 5-minute intervals and perform emergency shut-down per Section 4.5 if temperature rises above 90 °C.

### 7.4 High Bearing Temperature

**Associated error codes:** E-201 (DE warning), E-202 (NDE warning), E-203 (DE alarm), E-204 (lubrication low)

**Symptom:** Bearing housing temperature elevated above the warning or alarm threshold. This section covers high temperature without a corresponding high-vibration signature (high temperature + high vibration is addressed in Section 7.3).

**Possible causes and diagnostic steps:**

| Probable Cause | Diagnostic Check | Action |
|---|---|---|
| Low oil level | Check sight glass | Top up per Section 5.3; investigate cause of oil loss |
| Contaminated oil | Drain sample; inspect for milkiness or sludge | Change oil per Section 5.3; investigate contamination source |
| Wrong oil grade | Check oil viscosity on filler cap label | Drain and refill with approved ISO VG 46 |
| Overfilled housing | Sight glass shows oil at or above top mark | Drain excess oil to mid-level |
| Excessive ambient temperature | Check ambient at bearing housing; must be ≤ 40 °C | Improve ventilation or install cooling fan |
| Incorrect preload (after reassembly) | Compare against bearing installation records | Adjust preload per workshop manual |

> **CAUTION:** Bearing temperature must not exceed 90 °C under any circumstances. Above 90 °C, ISO VG 46 mineral oil viscosity drops below the minimum film thickness required for hydrodynamic lubrication, causing metal-to-metal contact and bearing seizure.

**Lockout requirement before oil change:**

Before removing the oil filler plug or drain plug on a running or recently stopped machine, note that the shaft is in close proximity to the bearing housing access points. Always lock out the motor circuit before any hands-on contact with the bearing housing (see Section 6.1 and Section 5.3).

### 7.5 Motor Overload and Electrical Faults

**Associated error codes:** E-301 (overload trip), E-302 (phase loss), E-303 (phase imbalance), E-304 (thermal protection), E-305 (starter fault)

**Symptom:** The motor protective relay has tripped; the pump is not running. The MCC indicates an overload, phase-loss, or thermal fault. Motor may feel hot to the touch.

> **DANGER:** Do not reset an overload relay and restart the motor without first identifying and correcting the cause of the trip. Repeated tripping is a symptom of an underlying mechanical or electrical fault. Forcing a restart may cause motor winding failure, fire, or explosion.

**Diagnostic procedure:**

1. Record the overload relay trip class and the current at trip from the relay display.
2. Check that the fault is not a nuisance trip caused by a momentary voltage sag. If the relay has an event log, confirm whether the trip occurred at full motor current (true overload) or at low current (phase loss).
3. For overload (E-301): Before resetting, manually turn the pump shaft. If the shaft is stiff or will not turn, a mechanical seizure (bearing, impeller rubbing, or foreign object) is present. Do not start until the mechanical cause is cleared.
4. For phase loss (E-302): Use a multimeter to measure voltage at all three phases at the motor terminals. A reading of zero (or substantially reduced) on one phase indicates a blown fuse, open contactor contact, or cable fault.
5. For phase imbalance (E-303): Measure phase voltages at the motor terminal box with the motor de-energised. Voltage imbalance above 2 % requires investigation at the MCC distribution panel.
6. For thermal protection trip (E-304): Allow the motor to cool for at least 30 minutes before re-energising. Investigate the cause of overheating (blocked motor cooling fan, high ambient, overload condition) before restart.
7. If the motor restarts and trips again within one hour, the fault has not been corrected. Raise a maintenance work order for motor and starter inspection.

**Electrical isolation before inspection:**

> **WARNING:** Perform full lockout/tagout per Section 6.1 before inspecting motor terminal connections, contactor contacts, overload relay wiring, or cable insulation. Voltages in the MCC may be present from adjacent feeders even when the pump circuit breaker is open.

### 7.6 High Differential Pressure — Clogged Filter

**Associated error codes:** E-111

**Symptom:** The suction strainer differential pressure (ΔP) gauge or SCADA alarm indicates ΔP above 0.3 bar. Flow rate may be reduced. Suction pressure may be low, compounding any existing cavitation risk.

**Diagnostic procedure:**

1. Read the strainer ΔP gauge. A reading between 0.2 and 0.3 bar indicates partial blinding; a reading above 0.3 bar indicates a significantly clogged element. Both conditions require planned strainer service.
2. Check the upstream process for abnormal solids loading (pipe scale, biological fouling, debris from upstream maintenance, or seasonal suspended solids increase).
3. Shut down the pump and service the suction strainer per Section 5.5.
4. After servicing, check the ΔP gauge reads below 0.1 bar with the pump running at rated flow.
5. If the element clogs rapidly (within 24 hours), increase the service frequency and investigate the source of debris.

> **NOTICE:** The suction strainer differential pressure alarm threshold (E-111 trigger) is pre-set at 0.3 bar from the factory. This can be adjusted in the SCADA tag configuration to match site-specific conditions; consult the Reliability Engineer before changing alarm setpoints.

---

## 8. Error Code Reference Table

The following error codes are generated by the Motor Control Panel (MCP) and/or the SCADA system. All codes are latching and must be cleared manually after the fault condition is resolved.

| Code | Meaning | Probable Causes | Cross-Reference |
|---|---|---|---|
| E-101 | Suction pressure low — warning | Suction valve partially closed, strainer partially clogged, pipe restriction | Section 7.1 |
| E-102 | Cavitation detected | Insufficient NPSH, suction pipe vapour lock, high fluid temperature, low suction pressure | Section 7.1 |
| E-103 | Discharge pressure high — alarm | Closed or restricted discharge valve, blocked discharge pipe, downstream valve closed | Section 4.2, 4.4 |
| E-104 | Discharge pressure low — warning | Impeller wear, incorrect rotation, cavitation, coupling failure | Section 7.1 |
| E-105 | Shaft vibration — misalignment signature | Shaft misalignment after maintenance, worn coupling insert, soft-foot | Section 7.2 |
| E-106 | Suction fluid temperature high | Process temperature excursion upstream; check source | Section 4.3 |
| E-107 | Drive-end bearing vibration — alarm | Bearing degradation, spalling, contaminated lubricant, incorrect preload | Section 7.3 |
| E-108 | Non-drive-end bearing vibration — alarm | Same as E-107 for non-drive-end bearing | Section 7.3 |
| E-109 | Flow rate low — alarm | Suction restriction, impeller wear, cavitation, closed discharge | Section 7.1 |
| E-110 | Flow rate high — alarm | Operating beyond BEP; cavitation risk at high flow; valve misoperation | Section 4.2 |
| E-111 | Suction strainer ΔP high | Clogged strainer element, debris ingestion, biological fouling | Section 7.6, 5.5 |
| E-112 | Mechanical seal leak detected | Seal face contamination, thermal shock, loss of flush, end-of-service-life | Section 5.6 |
| E-201 | Drive-end bearing temperature — warning | Low oil, incorrect oil grade, bearing wear beginning | Section 7.4, 5.3 |
| E-202 | Non-drive-end bearing temperature — warning | Same as E-201 for non-drive-end | Section 7.4 |
| E-203 | Drive-end bearing temperature — alarm | Severe lubrication failure, bearing imminent failure | Section 7.3, 7.4 |
| E-204 | Lubrication pressure / oil level low | Oil loss through seal leak, drain plug loose, extended interval without top-up | Section 5.3 |
| E-205 | Bearing oil temperature high | Incorrect oil grade, foaming, blocked oil passage | Section 5.3 |
| E-301 | Motor current high — overload trip | Mechanical seizure, impeller clog, high fluid density, overloaded operating point | Section 7.5 |
| E-302 | Motor current low — phase loss | Blown fuse, open contactor, cable fault | Section 7.5, 6.3 |
| E-303 | Phase imbalance detected | Unbalanced supply voltage, loose terminal connection | Section 7.5, 6.3 |
| E-304 | Motor thermal protection trip | Sustained overload, high ambient, blocked cooling fan | Section 7.5 |
| E-305 | Motor starter fault | Contactor mechanical fault, coil failure, control circuit fault | Section 6.1 |

---

## 9. Parts List and Ordering

Refer to the Synthetix Fluid Systems Parts Catalogue (document PCat-CP450-C) for full exploded-view drawings and part numbers. Critical spare parts recommended for 12-month stock holding:

| Part Description | Synthetix Part No. | Quantity |
|---|---|---|
| Drive-end bearing SKF 6209-2RS | SFL-BRG-6209-2RS | 2 |
| Non-drive-end bearing SKF 6207-2RS | SFL-BRG-6207-2RS | 2 |
| Cartridge mechanical seal SFT-CS100 | SFL-SEAL-CS100 | 1 |
| Coupling insert (rubber spider) | SFL-CUP-INS-450 | 2 |
| Suction strainer basket (316 SS, 1.6 mm) | SFL-STR-BSKT-450 | 1 |
| Impeller wear ring (bronze) | SFL-WR-IMP-450 | 1 |
| Casing wear ring (cast iron) | SFL-WR-CSG-450 | 1 |
| Bearing housing O-ring set | SFL-OR-BH-450 | 2 sets |
| Drain plug (1/2" NPT stainless) | SFL-PLUG-DN-450 | 2 |
| Seal flush line filter element | SFL-FFE-450 | 4 |

---

## 10. Revision History

| Revision | Date | Changes | Authorised By |
|---|---|---|---|
| Rev A | 2018-06-01 | Initial release | J. Hartley, Chief Engineer |
| Rev B | 2021-09-01 | Updated bearing specs (SKF to ZKL changeover reversed); added E-303/E-304/E-305 codes; updated torque table | M. Okafor, Technical Author |
| Rev C | 2024-03-15 | LOTO procedure updated to align with ISO 45001:2018; added E-111 strainer alarm; Section 7.6 added; Section 6 rewritten to include MCC ESSOW requirements; oil change interval reduced from 6 months to 3 months (field feedback) | S. Kapoor, Reliability Engineering |

---

*End of CP-450 Centrifugal Pump Service Manual, Rev C*  
*Document Number: MAN-CP450-SVC-C | © 2024 Synthetix Fluid Systems Ltd. All rights reserved.*  
*Reproduction of any part of this document without written permission is prohibited.*
