from res.enkf import ErtImplType, GenKwConfig


CONFIG = "Equinor/config/with_data/config"


def test_gen_kw_config(ert_data):
    with ert_data(CONFIG_PATH) as context:
        ert = context.getErt()

        result_gen_kw_keys = ert.ensembleConfig().getKeylistFromImplType(ErtImplType.GEN_KW)

        expected_keys = ["GRID_PARAMS", "FLUID_PARAMS", "MULTFLT"]

        assert set(result_gen_kw_keys) == set(expected_keys)
        assert len(expected_keys) == len(result_gen_kw_keys)

        for key in expected_keys:
            node = ert.ensembleConfig().getNode(key)
            gen_kw_config = node.getModelConfig()
            assert isinstance(gen_kw_config, GenKwConfig)

            assert gen_kw_config.getKey() == key

            if key == "GRID_PARAMS":
                expected_values = ["MULTPV2", "MULTPV3"]

                assert not gen_kw_config.shouldUseLogScale(0)
                assert not gen_kw_config.shouldUseLogScale(1)

            elif key == "MULTFLT":
                expected_values = ["F3"]

                assert gen_kw_config.shouldUseLogScale(0)

            elif key == "FLUID_PARAMS":
                expected_values = ["SWCR", "SGCR"]
                assert not gen_kw_config.shouldUseLogScale(0)
                assert not gen_kw_config.shouldUseLogScale(1)

            assert list(gen_kw_config) == expected_values
