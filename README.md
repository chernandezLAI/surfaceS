# surfaceS
surfaceS is a control and visualization tool for surface vibration analysis.

**Author:** [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)

## State of the project

## Project

The EPFL – LAI is investigating novel haptic technologies for rendering rich vibrotactile feedback in
digital musical interfaces. The main objective is to develop an interactive surface that is able to render
a multi-touch vibrotactile stimulus using piezoelectric actuators and wave focusing strategies.
Scanning the surface to obtain the peaks and displacement is key during the development and
characterization of the whole system.

The goal of this project is to develop a system that can measure small vibrations (in the order of 2 – 20
um) that are produced in the different points of a surface, when different waveforms are transmitted
to the surface using piezoelectric transducers.
This project will allow you to get hands-on experience with the software and hardware integration of
a 3-axis CNC table, a waveform generator, a laser Doppler vibrometer, and an oscilloscope.
Objectives of the work

The objectives of the project are to:
- Understand the different measurement techniques for surface vibration.
- Assemble and commission a 3-axis CNC table.
- Implement the software integration of a waveform generator, signal amplifier, oscilloscope, compact laser vibrometer and 3-axis CNC table.
- Define and implement the user interface for setting the measurement parameters (i.e. size of the area to measure, number of points to measure, waveform to send to the plate, ...) and plotting the measured vibrations obtained in the area of the surface.
- Test the whole system with a provided waveform.
- Develop an operational manual for the application.

### Report

The final report will contain the following points:
- A state of the art in surface vibration measuring techniques.
- The functional diagram, the operational manual, and the source code of the final implementation.

Supervisors: Camilo Hernandez M., Paolo Germano - Professor: Yves Perriard

## Useful commands

To generate python class for the UI:

> pyuic5 surfaceS\ui\mainwindow.ui -o surfaceS\ui\mainwindow.py

## GRBL controller parameters
´´
CNCjs 1.9.15 [Grbl]
Connected to COM5 with a baud rate of 115200
Grbl 1.1g ['$' for help]
client> $$
[MSG:'$H'|'$X' to unlock]
$0=10 (Step pulse time, microseconds)
$1=200 (Step idle delay, milliseconds)
$2=0 (Step pulse invert, mask)
$3=0 (Step direction invert, mask)
$4=1 (Invert step enable pin, boolean)
$5=1 (Invert limit pins, boolean)
$6=0 (Invert probe pin, boolean)
$10=1 (Status report options, mask)
$11=0.010 (Junction deviation, millimeters)
$12=0.002 (Arc tolerance, millimeters)
$13=0 (Report in inches, boolean)
$20=0 (Soft limits enable, boolean)
$21=1 (Hard limits enable, boolean)
$22=1 (Homing cycle enable, boolean)
$23=1 (Homing direction invert, mask)
$24=120.000 (Homing locate feed rate, mm/min)
$25=900.000 (Homing search seek rate, mm/min)
$26=250 (Homing switch debounce delay, milliseconds)
$27=2.000 (Homing switch pull-off distance, millimeters)
$30=1000 (Maximum spindle speed, RPM)
$31=0 (Minimum spindle speed, RPM)
$32=0 (Laser-mode enable, boolean)
$100=133.333 (X-axis travel resolution, step/mm)
$101=133.333 (Y-axis travel resolution, step/mm)
$102=133.333 (Z-axis travel resolution, step/mm)
$110=3000.000 (X-axis maximum rate, mm/min)
$111=3000.000 (Y-axis maximum rate, mm/min)
$112=3000.000 (Z-axis maximum rate, mm/min)
$120=10.000 (X-axis acceleration, mm/sec^2)
$121=10.000 (Y-axis acceleration, mm/sec^2)
$122=10.000 (Z-axis acceleration, mm/sec^2)
$130=422.000 (X-axis maximum travel, millimeters)
$131=131.000 (Y-axis maximum travel, millimeters)
$132=142.000 (Z-axis maximum travel, millimeters)
ok
´´
