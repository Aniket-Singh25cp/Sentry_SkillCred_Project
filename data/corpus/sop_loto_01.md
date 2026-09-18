# SOP-LOTO-01: Lockout/Tagout Procedure

**Document Number:** SOP-LOTO-01  
**Revision:** Rev E  
**Issue Date:** 2024-01-10  
**Approved By:** A. Mensah, EHS Manager  
**Regulatory Basis:** ISO 45001:2018, OSHA 29 CFR 1910.147, IEC 60364-4-46  
**Asset Classes:** centrifugal_pump, industrial_gearbox (and all other plant machinery)  

---

> **DANGER:** Never attempt to perform lockout/tagout unless you have been trained, tested, and authorised under the plant Lockout/Tagout Programme. Unauthorised individuals must not apply or remove locks under any circumstances.

> **DANGER:** Lockout/tagout failure is a leading cause of industrial fatalities. In 2019, OSHA estimated that proper LOTO prevents approximately 120 worker deaths and 50 000 injuries annually in the United States alone. Do not shortcut this procedure under any circumstances, including time pressure, management pressure, or perceived urgency.

---

## 1. Purpose and Scope

This SOP defines the mandatory procedure for controlling hazardous energy before any maintenance, servicing, or inspection of equipment in which the unexpected energisation, start-up, or release of stored energy could cause injury or death.

Hazardous energy types covered by this SOP include:
- **Electrical energy:** Three-phase LV (up to 1 000 V AC), single-phase circuits, UPS-backed circuits, and control voltage circuits.
- **Mechanical energy:** Kinetic energy of rotating components (flywheels, pump impellers, gearbox gear sets, conveyor drives); stored spring or tension energy.
- **Hydraulic energy:** Pressurised hydraulic lines and accumulators.
- **Pneumatic energy:** Compressed air systems and pneumatic actuators.
- **Thermal energy:** Hot surfaces, steam, and hot oil systems.
- **Gravitational energy:** Suspended loads, counter-weighted doors, and raised equipment on jacks.

This procedure does not cover High Voltage (HV) systems (above 1 000 V AC), which are covered by the site High Voltage Safety Rules document (HVSR-001).

---

## 2. Definitions

| Term | Definition |
|---|---|
| **Authorised Person (AP)** | A person who has been trained and assessed as competent to perform LOTO, and whose name appears on the site LOTO authorisation register. |
| **Responsible Person (RP)** | The Authorised Person who is accountable for the safety of the work; issues the Permit to Work (PTW). |
| **Affected Person** | Anyone who works in an area where LOTO is in use; they do not need to be authorised but must know they must not operate the isolated equipment. |
| **Permit to Work (PTW)** | Written authority confirming the work may begin after isolation. |
| **Danger Tag** | A red tag attached to a lockout point stating the equipment must not be operated. Not a substitute for a lock. |
| **Personal Safety Lock** | A padlock that only the individual technician can remove, using a unique key held only by that person. |
| **Hasp** | A multi-lock device that allows several personal locks to be fitted to a single lockout point simultaneously. |
| **Zero-Energy State** | Confirmed condition where all hazardous energy sources have been isolated and residual energy dissipated. |

---

## 3. Responsibilities

- **Every Authorised Person** must apply their own personal lock. Lock application must never be delegated.
- **The Responsible Person** must ensure all energy sources for the equipment are identified before issuing the PTW.
- **All Affected Persons** must be briefed that LOTO is in place before work begins.
- **The EHS Manager** maintains the LOTO authorisation register and ensures annual refresher training for all APs.

---

## 4. Lockout/Tagout Procedure — Step by Step

### 4.1 Preparation

**Procedure LOTO-A — Preparation:**

1. Obtain the PTW from the Responsible Person. Confirm the PTW identifies all energy sources for the equipment.
2. Obtain the LOTO equipment kit: personal padlock (with key retained on your person), danger tag, hasp (for group LOTO), and cable lock (for breakers requiring cable locking).
3. Notify all affected persons in the work area that LOTO is being applied and the equipment must not be operated.
4. Obtain the current operational state of the equipment from the shift supervisor or control room. Confirm the equipment is stopped or can be safely stopped.

### 4.2 Shutdown

**Procedure LOTO-B — Shutdown:**

1. Stop the equipment using its normal stopping procedure (see the relevant equipment manual, e.g., Section 4.4 of MAN-CP450-SVC-C for centrifugal pumps).
2. Confirm the equipment has reached a stationary state. For rotating equipment, wait until all rotation has ceased; do not assume a de-energised motor has stopped immediately.
3. For pressurised systems: close the nearest upstream isolation valve. Vent pressure via the designated vent point to atmosphere. Confirm pressure gauge reads zero.

### 4.3 Isolation

**Procedure LOTO-C — Isolation:**

For all applicable energy sources identified on the PTW, perform isolation in the following order:

1. **Electrical isolation:**
   a. At the motor control centre, identify the correct feeder circuit breaker by comparing the circuit label with the work order and equipment asset tag.
   b. Turn the circuit breaker to the OFF position.
   c. If a motor isolation switch (local disconnect) is fitted at the equipment, turn it to the OFF or LOCKED-OFF position as well.

2. **Mechanical isolation:**
   a. For equipment that can be driven by an external mechanism (e.g., a pump driven by a generator via a coupling): ensure the driving machine is also locked out before working on the driven machine.
   b. Block or support any equipment that could move under gravity (e.g., a vertically-mounted pump impeller, a raised gate valve, a suspended load).

3. **Hydraulic/pneumatic isolation:**
   a. Close and lock the isolation valve in the hydraulic or pneumatic supply line.
   b. Vent residual pressure to a safe location.
   c. If an accumulator is present, confirm it is depressurised per the manufacturer's instructions before proceeding.

4. **Thermal isolation:**
   a. Close and lock the steam or hot-fluid supply valve.
   b. Allow the system to cool to below 40 °C before physical contact with pipework or equipment surfaces.

### 4.4 Lock and Tag Application

**Procedure LOTO-D — Apply Locks and Tags:**

1. Apply your personal padlock to the lockout hasp on the circuit breaker. If multiple technicians are working on the same equipment, each must apply their own padlock to the same hasp. Do not share locks.
2. Retain the key to your padlock on your person at all times while work is in progress. Do not leave the key in the lock, hang it nearby, or give it to another person.
3. Attach a danger tag to each locked-out isolation point. The tag must show:
   - Your full name
   - Date and time of application
   - Work order number
   - Contact number
   - The warning: "DO NOT OPERATE — PEOPLE AT RISK"
4. For group LOTO with a group safety box: each technician locks their personal key into the group safety box. One additional lock on the group box requires all personal keys to be returned before the group box can be opened.

> **WARNING:** A danger tag alone, without a lock, is not a safe isolation. Tags can be ignored, accidentally removed, or deliberately disregarded. A lock physically prevents operation of the isolation device. Never rely on a tag without a lock.

### 4.5 Verification of Zero-Energy State

**Procedure LOTO-E — Zero-Energy Verification:**

> **DANGER:** Verification of zero energy must never be skipped, even if the person applying the lock is certain the circuit was de-energised. Parallel feeds, backfeed from other equipment, and energised control circuits can maintain lethal voltage after the main breaker is opened.

1. Using a calibrated dual-function voltage tester (IEC 61243-3), verify the absence of voltage at the motor terminal box:
   - First, prove the tester is live (measure a known live source).
   - Measure all three phase-to-phase combinations (U-V, V-W, W-U) at the motor terminals.
   - Measure all three phases to earth.
   - Second, prove the tester is still live (measure the known live source again).
   - If any phase reads > 0 V, the isolation is incomplete. Do not proceed. Investigate and correct.
2. Attempt to start the motor from the local control panel. Confirm the motor does not start and no voltage appears.
3. For pressurised systems, confirm all pressure gauges read zero and are not blocked.
4. For mechanical energy: attempt to rotate the shaft by hand. Confirm there is no driving force tending to rotate it.
5. Record the zero-energy verification in the PTW.

---

## 5. Restoration of Energy (Return to Service)

> **WARNING:** Energy must not be restored until ALL personnel are confirmed clear of the equipment, ALL covers and guards are in place, and ALL tools and foreign objects have been removed.

**Procedure LOTO-F — Restoration:**

1. Inspect the equipment to confirm all maintenance work is complete:
   - All tools, materials, and rags removed.
   - All covers, guards, and fasteners replaced and torqued.
   - All drain plugs and filler plugs replaced.
   - All instrumentation and pipework reconnected.
2. Each technician confirms they are clear of the equipment and removes their personal padlock from the hasp. The last padlock on the hasp may only be removed when all other padlocks have been removed.
3. Remove the danger tag from each isolation point.
4. The Responsible Person performs a final check and signs off the PTW as complete.
5. The circuit breaker is closed only by the Authorised Person who performed the isolation, or by another AP at the direction of the RP after the PTW is signed off.
6. Perform the equipment pre-start checklist before starting (see the relevant equipment manual).

---

## 6. Special Situations

### 6.1 Shift Handover During LOTO

If LOTO extends across a shift change:
1. The outgoing technician must transfer their personal lock to the incoming technician's personal lock before removing theirs, ensuring the lockout point is never unprotected.
2. Both the outgoing and incoming technician must sign the handover section of the PTW.
3. The incoming technician takes personal responsibility for the lockout from the moment of handover.

### 6.2 Emergency Removal of a Lock

If a technician leaves the site without removing their personal lock, and work must be resumed:
1. The site EHS Manager must be notified.
2. A documented emergency lock-removal procedure must be followed (see ESSOW-EM-001).
3. The technician's supervisor must confirm the technician is not in the hazard area.
4. The EHS Manager or delegate may then cut the lock under documented supervision.
5. The technician must be contacted and the incident investigated.

> **DANGER:** Emergency lock removal may only be authorised by the EHS Manager or their designated deputy. Cutting a lock without authorisation is a disciplinary offence and may constitute a criminal breach of workplace safety law.

### 6.3 Complex LOTO (Multiple Energy Sources)

For equipment with more than four energy sources, a Complex LOTO Worksheet must be prepared in advance by the Responsible Person. The worksheet lists every energy source, the isolation point, the isolation method, and the person who performed each isolation. Each isolation must be independently verified.

---

## 7. Training and Authorisation

All Authorised Persons must:
- Complete the Synthetix LOTO Training Module (online, 90 minutes) before their first LOTO application.
- Complete a practical assessment supervised by a currently-authorised AP.
- Renew authorisation annually via a 30-minute refresher module and a practical re-assessment.
- Their name must appear on the current LOTO Authorisation Register (controlled by EHS).

Workers who are not authorised must not apply or remove LOTO devices. They must report any LOTO device they find in an unexpected state to their supervisor immediately.

---

## 8. Audit and Compliance

EHS will conduct unannounced LOTO audits at a minimum frequency of once per month. Audits assess:
- Correct lock and tag application (personal lock, matching tag, all energy sources isolated).
- Zero-energy verification performed and recorded.
- Affected persons notified.
- PTW correctly filled in and signed.

Non-conformances are categorised as Critical (lock missing), Major (tag missing or incorrect), or Minor (record incomplete). A Critical non-conformance results in immediate work stoppage and an investigation per the site incident management procedure.

---

## 9. Revision History

| Revision | Date | Changes | Authorised By |
|---|---|---|---|
| Rev A | 2016-03-01 | Initial issue | T. Osei, EHS |
| Rev B | 2018-07-15 | Added complex LOTO section; updated VSD guidance | T. Osei, EHS |
| Rev C | 2020-11-01 | Full rewrite to align with ISO 45001:2018 | A. Mensah, EHS |
| Rev D | 2022-06-10 | Added shift handover procedure; emergency lock removal reference to ESSOW-EM-001 | A. Mensah, EHS |
| Rev E | 2024-01-10 | Updated definitions; added OSHA 1910.147 reference; compliance section added | A. Mensah, EHS |

---

*End of SOP-LOTO-01, Rev E*  
*Document Number: SOP-LOTO-01 | © 2024 Synthetix Fluid Systems Ltd. All rights reserved.*  
*This document is subject to mandatory annual review.*
