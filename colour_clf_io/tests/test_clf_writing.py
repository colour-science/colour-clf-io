"""Define the unit tests for the :mod:`colour.io.clf` module."""

from __future__ import annotations

import os

import colour_clf_io.elements
import colour_clf_io.process_nodes
import colour_clf_io.values
from colour_clf_io import read_clf, write_clf

from .test_clf_common import wrap_snippet

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "ROOT_CLF",
    "EXAMPLE_WRAPPER",
    "TestWriteCLF",
]

ROOT_CLF: str = os.path.join(os.path.dirname(__file__), "resources")

EXAMPLE_WRAPPER: str = """<?xml version="1.0" ?>
<ProcessList xmlns="urn:AMPAS:CLF:v3.0" id="Example Wrapper" compCLFversion="2.0">
{0}
</ProcessList>
"""


def assert_valid_roundtrip_for_snippet(example: str) -> None:
    doc_original = wrap_snippet(example)
    assert_valid_roundtrip_for_doc(doc_original)


def assert_valid_roundtrip_for_file(path: str) -> None:
    with open(path) as f:
        file_content = f.read()
        assert_valid_roundtrip_for_doc(file_content)


def assert_valid_roundtrip_for_doc(doc: str) -> None:
    doc_original = read_clf(doc)
    assert doc_original is not None
    xml = write_clf(doc_original)
    assert xml is not None
    doc_after_roundtrip = read_clf(xml)
    assert doc_original == doc_after_roundtrip


class TestWriteCLF:
    """
    Define tests methods for parsing *CLF* files using the functionality
    provided in the :mod: `colour.io.clf`module.
    """

    def test_sample_document_1(self) -> None:
        """
        Test parsing of the sample file `ACES2065_1_to_ACEScct.xml`.
        """

        path = os.path.join(ROOT_CLF, "ACES2065_1_to_ACEScct.xml")
        assert_valid_roundtrip_for_file(path)

    def test_read_sample_document_2(self) -> None:
        """
        Test parsing of the sample file `LMT Kodak 2383 Print Emulation.xml`.
        """
        path = os.path.join(ROOT_CLF, "LMT Kodak 2383 Print Emulation.xml")
        assert_valid_roundtrip_for_file(path)

    def test_read_sample_document_3(self) -> None:
        """
        Test parsing of the sample file `LMT_ARRI_K1S1_709_EI800_v3.xml`.
        """

        path = os.path.join(ROOT_CLF, "LMT_ARRI_K1S1_709_EI800_v3.xml")
        assert_valid_roundtrip_for_file(path)

    def test_LUT1D_example(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 1.
        """

        example = """
        <LUT1D id="lut-23" name="4 Value Lut" inBitDepth="12i" outBitDepth="12i">
            <Description>1D LUT - Turn 4 grey levels into 4 inverted codes</Description>
            <Array dim="4 1">
                3
                2
                1
                0
            </Array>
        </LUT1D>
        """
        assert_valid_roundtrip_for_snippet(example)

    def test_LUT3D_example(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 2.
        """

        example = """
        <LUT3D id="lut-24" name="green look" interpolation="trilinear" inBitDepth="12i" outBitDepth="16f">
            <Description>3D LUT</Description>
            <Array dim="2 2 2 3">
                0.0 0.0 0.0
                0.0 0.0 1.0
                0.0 1.0 0.0
                0.0 1.0 1.0
                1.0 0.0 0.0
                1.0 0.0 1.0
                1.0 1.0 0.0
                1.0 1.0 1.0
            </Array>
        </LUT3D>
        """  # noqa: E501

        assert_valid_roundtrip_for_snippet(example)

    def test_matrix_example_1(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 3.
        """

        example = """
        <Matrix id="lut-28" name="AP0 to AP1" inBitDepth="16f" outBitDepth="16f" >
            <Description>3x3 color space conversion from AP0 to AP1</Description>
            <Array dim="3 3">
                 1.45143931614567     -0.236510746893740    -0.214928569251925
                -0.0765537733960204    1.17622969983357     -0.0996759264375522
                 0.00831614842569772  -0.00603244979102103   0.997716301365324
            </Array>
        </Matrix>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_matrix_example_2(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 4.
        """

        example = """
        <Matrix id="lut-25" name="colorspace conversion" inBitDepth="10i" outBitDepth="10i" >
            <Description> 3x4 Matrix , 4th column is offset </Description>
            <Array dim="3 4">
                1.2     0.0     0.0     0.002
                0.0     1.03    0.001   -0.005
                0.004   -0.007  1.004   0.0
            </Array>
        </Matrix>
        """  # noqa: E501

        assert_valid_roundtrip_for_snippet(example)

    def test_range_example(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 5.
        """

        example = """
        <Range inBitDepth="10i" outBitDepth="10i">
            <Description>10-bit full range to SMPTE range</Description>
            <minInValue>0</minInValue>
            <maxInValue>1023</maxInValue>
            <minOutValue>64</minOutValue>
            <maxOutValue>940</maxOutValue>
        </Range>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_log_example_1(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 6.
        """

        example = """
        <Log inBitDepth="16f" outBitDepth="16f" style="log10">
            <Description>Base 10 Logarithm</Description>
        </Log>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_log_example_2(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 7.
        """

        example = """
        <Log inBitDepth="32f" outBitDepth="32f" style="cameraLinToLog">
            <Description>Linear to DJI D-Log</Description>
            <LogParams base="10" logSideSlope="0.256663" logSideOffset="0.584555"
                linSideSlope="0.9892" linSideOffset="0.0108" linSideBreak="0.0078"
                linearSlope="6.025"/>
        </Log>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_exponent_example_1(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 8.
        """

        example = """
        <Exponent inBitDepth="32f" outBitDepth="32f" style="basicFwd">
            <Description>Basic 2.2 Gamma</Description>
            <ExponentParams exponent="2.2"/>
        </Exponent>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_exponent_example_2(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 9.
        """

        example = """
        <Exponent inBitDepth="32f" outBitDepth="32f" style="monCurveFwd">
            <Description>EOTF (sRGB)</Description>
            <ExponentParams exponent="2.4" offset="0.055" />
        </Exponent>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_exponent_example_3(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 10.
        """

        example = """
        <Exponent inBitDepth="32f" outBitDepth="32f" style="monCurveRev">
            <Description>CIE L*</Description>
            <ExponentParams exponent="3.0" offset="0.16" />
        </Exponent>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_exponent_example_4(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 11.
        """

        example = """
         <Exponent inBitDepth="32f" outBitDepth="32f" style="monCurveRev">
            <Description>Rec. 709 OETF</Description>
            <ExponentParams exponent="2.2222222222222222" offset="0.099" />
        </Exponent>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_ASC_CDL_example(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 12.
        """

        example = """
        <ASC_CDL id="cc01234" inBitDepth="16f" outBitDepth="16f" style="Fwd">
            <Description>scene 1 exterior look</Description>
            <SOPNode>
                <Slope>1.000000 1.000000 0.900000</Slope>
                <Offset>-0.030000 -0.020000 0.000000</Offset>
                <Power>1.2500000 1.000000 1.000000</Power>
            </SOPNode>
            <SatNode>
                <Saturation>1.700000</Saturation>
            </SatNode>
        </ASC_CDL>
        """

        assert_valid_roundtrip_for_snippet(example)

    def test_ACES2065_1_to_ACEScg_example(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 13.
        """

        # Note that this string uses binary encoding, as the XML document specifies its
        # own encoding.
        example = b"""<?xml version="1.0" encoding="UTF-8"?>
        <ProcessList id="ACEScsc.ACES_to_ACEScg.a1.0.3" name="ACES2065-1 to ACEScg"
            compCLFversion="3.0">
            <Info>
                <ACEStransformID>ACEScsc.ACES_to_ACEScg.a1.0.3</ACEStransformID>
                <ACESuserName>ACES2065-1 to ACEScg</ACESuserName>
            </Info>
            <Description>ACES2065-1 to ACEScg</Description>
            <InputDescriptor>ACES2065-1</InputDescriptor>
            <OutputDescriptor>ACEScg</OutputDescriptor>
            <Matrix inBitDepth="16f" outBitDepth="16f">
                <Array dim="3 3">
                     1.451439316146 -0.236510746894 -0.214928569252
                    -0.076553773396  1.176229699834 -0.099675926438
                     0.008316148426 -0.006032449791  0.997716301365
                </Array>
            </Matrix>
        </ProcessList>
        """

        doc = read_clf(example)

        assert doc is not None

        assert len(doc.process_nodes) == 1
        assert isinstance(doc.process_nodes[0], colour_clf_io.process_nodes.Matrix)

    def test_ACES2065_1_to_ACEScct_example(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 14.
        """

        # Note that this string uses binary encoding, as the XML document specifies its
        # own encoding.
        example = b"""<?xml version="1.0" encoding="UTF-8"?>
        <ProcessList id="ACEScsc.ACES_to_ACEScct.a1.0.3" name="ACES2065-1 to ACEScct"
            compCLFversion="3.0">
            <Description>ACES2065-1 to ACEScct Log working space</Description>
            <InputDescriptor>Academy Color Encoding Specification (ACES2065-1)</InputDescriptor>
            <OutputDescriptor>ACEScct Log working space</OutputDescriptor>
            <Info>
                <ACEStransformID>ACEScsc.ACES_to_ACEScct.a1.0.3</ACEStransformID>
                <ACESuserName>ACES2065-1 to ACEScct</ACESuserName>
            </Info>
            <Matrix inBitDepth="16f" outBitDepth="16f">
                <Array dim="3 3">
                     1.451439316146 -0.236510746894 -0.214928569252
                    -0.076553773396  1.176229699834 -0.099675926438
                     0.008316148426 -0.006032449791  0.997716301365
                </Array>
            </Matrix>
            <Log inBitDepth="16f" outBitDepth="16f" style="cameraLinToLog">
                <LogParams base="2" logSideSlope="0.05707762557" logSideOffset="0.5547945205"
                    linSideBreak="0.0078125" />
            </Log>
        </ProcessList>
        """  # noqa: E501

        doc = read_clf(example)

        assert doc is not None

        assert len(doc.process_nodes) == 2
        assert isinstance(doc.process_nodes[0], colour_clf_io.process_nodes.Matrix)
        assert isinstance(doc.process_nodes[1], colour_clf_io.process_nodes.Log)

    def test_CIE_XYZ_to_CIELAB_example(self) -> None:
        """
        Test parsing of the example process node from the official *CLF* specification
        Example 14.
        """

        # Note that this string uses binary encoding, as the XML document specifies its
        # own encoding.
        example = b"""<?xml version="1.0" encoding="UTF-8"?>
        <ProcessList id="5ac02dc7-1e02-4f87-af46-fa5a83d5232d" compCLFversion="3.0">
            <Description>CIE-XYZ D65 to CIELAB L*, a*, b* (scaled by 1/100, neutrals at
                0.0 chroma)</Description>
            <InputDescriptor>CIE-XYZ, D65 white (scaled [0,1])</InputDescriptor>
            <OutputDescriptor>CIELAB L*, a*, b* (scaled by 1/100, neutrals at 0.0
                chroma)</OutputDescriptor>
            <Matrix inBitDepth="16f" outBitDepth="16f">
                <Array dim="3 3">
                    1.052126639 0.000000000 0.000000000
                    0.000000000 1.000000000 0.000000000
                    0.000000000 0.000000000 0.918224951
                </Array>
            </Matrix>
            <Exponent inBitDepth="16f" outBitDepth="16f" style="monCurveRev">
                <ExponentParams exponent="3.0" offset="0.16" />
            </Exponent>
            <Matrix inBitDepth="16f" outBitDepth="16f">
                <Array dim="3 3">
                    0.00000000  1.00000000  0.00000000
                    4.31034483 -4.31034483  0.00000000
                    0.00000000  1.72413793 -1.72413793
                </Array>
            </Matrix>
        </ProcessList>
        """

        doc = read_clf(example)

        assert doc is not None

        assert len(doc.process_nodes) == 3
        assert isinstance(doc.process_nodes[0], colour_clf_io.process_nodes.Matrix)
        assert isinstance(doc.process_nodes[1], colour_clf_io.process_nodes.Exponent)
        assert isinstance(doc.process_nodes[2], colour_clf_io.process_nodes.Matrix)
