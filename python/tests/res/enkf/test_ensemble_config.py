from tests import ResTest, tmpdir

from res.enkf import EnsembleConfig, ResConfig
from res.enkf import ConfigKeys
from res.enkf.enums import GenDataFileType


class EnsembleConfigTest(ResTest):
    def test_create(self):
        conf = EnsembleConfig( )
        assert len(conf) == 0
        assert not  "XYZ" in conf 

        with pytest.raises(KeyError):
            node = conf["KEY"]

    @tmpdir(local="configuration_tests")
    def test_ensemble_config_constructor(self):
        config_dict = {
            ConfigKeys.GEN_KW_TAG_FORMAT: '<%s>',
            ConfigKeys.GEN_PARAM: [
                {
                    ConfigKeys.NAME: 'GP',
                    ConfigKeys.FORWARD_INIT: False,
                    ConfigKeys.INPUT_FORMAT: GenDataFileType.ASCII,
                    ConfigKeys.OUTPUT_FORMAT: GenDataFileType.ASCII,
                    ConfigKeys.INIT_FILES: 'GP/GP.txt',
                    ConfigKeys.ECL_FILE: 'GP.txt',
                    ConfigKeys.MIN_STD: None,
                    ConfigKeys.TEMPLATE: None,
                    ConfigKeys.KEY_KEY: None
                },
            ],
            ConfigKeys.GEN_DATA: [
                {
                    ConfigKeys.NAME: 'SNAKE_OIL_OPR_DIFF',
                    ConfigKeys.INPUT_FORMAT: GenDataFileType.ASCII,
                    ConfigKeys.RESULT_FILE: 'snake_oil_opr_diff_%d.txt',
                    ConfigKeys.REPORT_STEPS: [199],
                    ConfigKeys.INIT_FILES: None,
                    ConfigKeys.ECL_FILE: None,
                    ConfigKeys.TEMPLATE: None,
                    ConfigKeys.KEY_KEY: None
                },
                {
                    ConfigKeys.NAME: 'SNAKE_OIL_GPR_DIFF',
                    ConfigKeys.INPUT_FORMAT: GenDataFileType.ASCII,
                    ConfigKeys.RESULT_FILE: 'snake_oil_gpr_diff_%d.txt',
                    ConfigKeys.REPORT_STEPS: [199],
                    ConfigKeys.INIT_FILES: None,
                    ConfigKeys.ECL_FILE: None,
                    ConfigKeys.TEMPLATE: None,
                    ConfigKeys.KEY_KEY: None
                }
            ],
            ConfigKeys.CUSTOM_KW: [
                {
                    ConfigKeys.NAME: 'SNAKE_OIL_NPV',
                    ConfigKeys.RESULT_FILE: 'snake_oil_npv.txt',
                    ConfigKeys.OUT_FILE: None
                }
            ],
            ConfigKeys.GEN_KW: [
                {
                    ConfigKeys.NAME: 'MULTFLT',
                    ConfigKeys.TEMPLATE: 'configuration_tests/FAULT_TEMPLATE',
                    ConfigKeys.OUT_FILE: 'MULTFLT.INC',
                    ConfigKeys.PARAMETER_FILE: 'configuration_tests/MULTFLT.TXT',
                    ConfigKeys.INIT_FILES: None,
                    ConfigKeys.MIN_STD: None,
                    ConfigKeys.FORWARD_INIT: False,
                }
            ],
            ConfigKeys.SURFACE_KEY: [
                {
                    ConfigKeys.NAME: 'TOP',
                    ConfigKeys.INIT_FILES: 'configuration_tests/surface/small.irap',
                    ConfigKeys.OUT_FILE: 'configuration_tests/surface/small_out.irap',
                    ConfigKeys.BASE_SURFACE_KEY: 'configuration_tests/surface/small.irap',
                    ConfigKeys.MIN_STD: None,
                    ConfigKeys.FORWARD_INIT: False
                }
            ],
            ConfigKeys.SUMMARY: ['WOPR:OP_1'],
            ConfigKeys.FIELD_KEY: [
                {
                    ConfigKeys.NAME: 'PERMX',
                    ConfigKeys.VAR_TYPE: 'PARAMETER',
                    ConfigKeys.INIT_FILES: 'fields/permx%d.grdecl',
                    ConfigKeys.OUT_FILE: 'permx.grdcel',
                    ConfigKeys.ENKF_INFILE: None,
                    ConfigKeys.INIT_TRANSFORM: None,
                    ConfigKeys.OUTPUT_TRANSFORM: None,
                    ConfigKeys.INPUT_TRANSFORM: None,
                    ConfigKeys.MIN_KEY: None,
                    ConfigKeys.MAX_KEY: None,
                    ConfigKeys.MIN_STD: None,
                    ConfigKeys.FORWARD_INIT: False
                }
            ],
            ConfigKeys.SCHEDULE_PREDICTION_FILE: [
                {
                    ConfigKeys.TEMPLATE: 'configuration_tests/input/schedule.sch',
                    ConfigKeys.INIT_FILES: None,
                    ConfigKeys.MIN_STD: None,
                    ConfigKeys.PARAMETER_KEY: None
                }
            ],
            ConfigKeys.CONTAINER_KEY: [
                {
                    ConfigKeys.NAME: 'CXX',
                    ConfigKeys.ARGLIST: ['PERMX', 'MULTFLT']
                }
            ]
        }

        res_config = ResConfig('configuration_tests/ensemble_config.ert')
        ensemble_config_file = res_config.ensemble_config
        ensemble_config_dict = EnsembleConfig(config_dict=config_dict, grid=res_config.ecl_config.getGrid())
        assert ensemble_config_dict == ensemble_config_file