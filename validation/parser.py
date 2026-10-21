#!/usr/bin/env python

# brachy-ir portal parser: metadata() reads the macro, parse() the "h20"
# 2D energy-deposition map (TH2F) written to brachytherapy.root, reduced to
# a radial relative-dose profile g(r).
#
# Ported from geant-config-generator/tests/geant4/brachy-ir/parser.py
# (gts.BaseParser, which merged repeated-seed jobs and shelled out to
# `root -l -b -q brachy_relative_dose.C`) to the module-level
# metadata()/parse() API expected by ci-workflows/validation/export.py. The
# radial-binning computation from brachy_relative_dose.C is reproduced
# directly with uproot (no ROOT binary, no PyROOT on the runner); there is
# no job-group merge any more — one macro means one run.
import math
import os

from geantval import getJSON, one_command, single_run

SOURCE_PARTICLE = {"Flexi": "Ir-192", "Oncura": "I-125",
                   "Leipzig": "Ir-192", "TG186": "Ir-192"}


def metadata(commands):
    single_run(commands)
    return {"TEST": "brachy-ir",
            "PHYSLIST": one_command(commands, "/testem/phys/addPhysics"),
            "SOURCE": one_command(commands, "/source/switch")}


def read_h20(path):
    import uproot

    with uproot.open(path) as root:
        hist = root["h20"]
        xcenters = hist.axis(0).centers(flow=False).tolist()
        ycenters = hist.axis(1).centers(flow=False).tolist()
        values = hist.values(flow=False)  # shape (801, 801)
    return xcenters, ycenters, values


def parse(job):
    xcenters, ycenters, values = read_h20(os.path.join(job["path"], "brachytherapy.root"))

    energy_map = [0.] * 401
    voxels = [0] * 401
    for ix, xx in enumerate(xcenters):
        row = values[ix]
        for iy, yy in enumerate(ycenters):
            radius = math.sqrt(xx * xx + yy * yy)  # mm
            if radius == 0.:
                continue
            rad_int = round(4 * radius)
            if 0 < rad_int <= 400:
                energy_map[rad_int] += float(row[iy])
                voxels[rad_int] += 1

    if voxels[40] == 0:
        raise ValueError("No energy deposited at the 1 cm / 90 deg reference point")
    norm = energy_map[40] / voxels[40]

    xvalues, yvalues = [], []
    for i in range(401):
        r_cm = i / 40.
        if r_cm <= 0.05:
            continue
        dose = energy_map[i] / voxels[i] / norm if voxels[i] > 0 else 0.
        xvalues.append(r_cm)
        yvalues.append(dose)

    rjson = getJSON(job, "chart",
                     mctool_name="GEANT4",
                     mctool_model=job["PHYSLIST"],
                     observableName="dose rate",
                     targetName="Water",
                     beamParticle=SOURCE_PARTICLE[job["SOURCE"]],
                     beamEnergies=[1., 2., 3., 4., 5.],
                     title="dose rate",
                     xAxisName="Distance from source (cm)",
                     yAxisName="Dose rate distribution g(r)",
                     xValues=xvalues,
                     yValues=yvalues)
    yield rjson
