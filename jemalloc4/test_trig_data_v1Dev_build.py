#!/usr/bin/env python
# Copyright (C) 2002-2021 CERN for the benefit of the ATLAS collaboration

# art-description: Trigger BS->RDO_TRIG athena test of the Dev_pp_run3_v1 menu
# art-type: build
# art-include: master/Athena
# Skipping art-output which has no effect for build tests.
# If you create a grid version, check art-output in existing grid tests.

from TrigValTools.TrigValSteering import Test, ExecStep, CheckSteps

ex = ExecStep.ExecStep()
ex.type = 'athena'
ex.job_options = 'TriggerJobOpts/runHLT_standalone.py'
ex.input = 'data'
ex.threads = 4
precommand = ''.join([
  "setMenu='LS2_v1_TriggerValidation_prescale';",  # LS2_v1 soon to be renamed to Dev_pp_run3_v1
  "doL1Sim=True;",
  "doWriteBS=False;",
  "doWriteRDOTrigger=True;",
  'doRuntimeNaviVal=True', # Perform runtime graph vaidation in this test
])
ex.args = '-c "{:s}" --stdcmalloc --preloadlib=/cvmfs/atlas.cern.ch/repo/sw/software/22.0/sw/lcg/releases/LCG_100_ATLAS_4/jemalloc/5.2.1/x86_64-centos7-gcc8-opt/lib/libjemalloc.so'.format(precommand)

test = Test.Test()
test.art_type = 'build'
test.exec_steps = [ex]
test.check_steps = CheckSteps.default_check_steps(test)

# Overwrite default MessageCount settings
# We are trying to lower the limits step by step
# Ultimately there should be no per-event messages
msgcount = test.get_step("MessageCount")
msgcount.thresholds = {
  'WARNING': 800,  # TODO: Fix the warnings and decrease the limit, ATR-23548, ATR-22942
  'INFO': 750,
  'other': 20
}
msgcount.required = True # make the test exit code depend on this step

# Add a step comparing counts against a reference
chaindump = test.get_step("ChainDump")
chaindump.args = '--json --yaml ref_data_v1Dev_build.new'
refcomp = CheckSteps.ChainCompStep("CountRefComp")
refcomp.input_file = 'ref_data_v1Dev_build.new'
refcomp.args += ' --patch'
refcomp.reference_from_release = True # installed from TriggerTest/share
refcomp.required = True # Final exit code depends on this step
CheckSteps.add_step_after_type(test.check_steps, CheckSteps.ChainDumpStep, refcomp)

import sys
sys.exit(test.run())
