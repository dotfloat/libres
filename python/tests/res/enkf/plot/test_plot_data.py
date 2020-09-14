import pytest

from tests import ResTest
from res.test import ErtTestContext

from res.enkf.plot_data import PlotBlockData, PlotBlockDataLoader, PlotBlockVector
from ecl.util.util import DoubleVector


CONFIG = "Equinor/config/with_RFT/config"


@pytest.mark.equinor_test
def test_plot_block_vector():
    vector = DoubleVector()
    vector.append(1.5)
    vector.append(2.5)
    vector.append(3.5)
    plot_block_vector = PlotBlockVector(1, vector)

    assert plot_block_vector.getRealizationNumber() == 1
    assert plot_block_vector[0] == 1.5
    assert plot_block_vector[2] == 3.5

    assert len(plot_block_vector) == len(vector)


@pytest.mark.equinor_test
def test_plot_block_data():
    depth = DoubleVector()
    depth.append(2.5)
    depth.append(3.5)

    data = PlotBlockData(depth)

    assert data.getDepth() == depth

    vector = PlotBlockVector(1, DoubleVector())
    data.addPlotBlockVector(vector)
    data.addPlotBlockVector(PlotBlockVector(2, DoubleVector()))

    assert len(data) == 2

    assert vector == data[1]


def checkBlockData(ert, obs_key, report_step):
    """
    @type ert: EnKFMain
    @type obs_key: str
    @type report_step: int
    """
    enkf_obs = ert.getObservations()
    obs_vector = enkf_obs[obs_key]
    loader = PlotBlockDataLoader(obs_vector)

    fs = ert.getEnkfFsManager().getCurrentFileSystem()
    plot_block_data = loader.load(fs, report_step)

    assert ert.getEnsembleSize() == len(plot_block_data)

    depth = plot_block_data.getDepth()

    depth_test_values = [1752.24998474, 1757.88926697, 1760.70924377]
    if report_step == 56:
        depth_test_values.append(1763.52885437)

    assert len(depth_test_values) == len(depth)
    for expect, actual in zip(depth_test_values, depth):
        assert expect == pytest.approx(actual)

    block_obs = len(obs_vector.getNode(report_step))
    assert block_obs == len(plot_block_data[0])
    assert block_obs == len(plot_block_data[9])


    if report_step == 50:
        rft_values = [244.681655884, 245.217041016, 245.48500061]
    else:
        rft_values = [239.7550354, 240.290313721, 240.558197021, 240.825881958]

    assert len(rft_values) == len(plot_block_data[0])
    for expect, actual in zip(rft_values, plot_block_data[0]):
        assert expect == pytest.approx(actual)


    if report_step == 50:
        rft_values = [238.702560425, 239.237838745, 239.505737305]
    else:
        rft_values = [234.41583252, 234.95098877, 235.218841553, 235.486480713]

    assert len(rft_values) == len(plot_block_data[9])
    for expect, actual in zip(rft_values, plot_block_data[9]):
        assert expect == pytest.approx(actual)


@pytest.mark.equinor_test
def test_plot_block_data_fs(datadir):
    with datadir.as_ert(CONFIG) as ert:
        checkBlockData(ert, "RFT2", 50)
        checkBlockData(ert, "RFT5", 56)
