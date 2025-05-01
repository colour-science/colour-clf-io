"""
Defines tests for validating XML generation against the SMPTE ST 2136-1 schema.
"""

from __future__ import annotations

from colour_clf_io import (
    ASC_CDL,
    LUT1D,
    LUT3D,
    Array,
    ASC_CDLStyle,
    BitDepth,
    CalibrationInfo,
    Channel,
    Exponent,
    ExponentParams,
    ExponentStyle,
    Info,
    Interpolation1D,
    Interpolation3D,
    Log,
    LogParams,
    LogStyle,
    Matrix,
    Namespaces,
    ProcessList,
    Range,
    RangeStyle,
    SatNode,
    SOPNode,
    write_clf,
)

from .test_clf_common import assert_valid_schema_schema_smtp_st2136_1

__author__ = "Colour Developers"
__copyright__ = "Copyright 2024 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["TestCLFXMLGeneration"]


class TestCLFXMLGeneration:
    """
    Define tests methods for validating XML generation against the SMPTE ST 2136-1
    schema.
    """

    def test_process_list_with_multiple_process_nodes_xml_generation(self) -> None:
        """
        Test that a ProcessList with multiple process nodes generates valid XML
        according to the schema.
        """
        matrix_array = Array(
            values=[
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
            ],
            dim=(3, 3),
        )

        matrix_node = Matrix(
            id="identity-matrix",
            name="Identity Matrix",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=matrix_array,
            description=["Identity matrix for testing"],
        )

        range_node = Range(
            id="range-node",
            name="Range Node",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            min_in_value=0.0,
            max_in_value=1.0,
            min_out_value=0.0,
            max_out_value=1.0,
            description=["Range transform for testing"],
            style=RangeStyle.CLAMP,
        )

        log_params = LogParams(
            base=10.0,
            log_side_slope=1.0,
            log_side_offset=0.0,
            lin_side_slope=1.0,
            lin_side_offset=0.0,
            lin_side_break=0.01,
            linear_slope=None,
            channel=None,
        )

        log_node = Log(
            id="log-node",
            name="Log Node",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            style=LogStyle.LOG_10,
            description=["Log10 transform for testing"],
            log_params=[log_params],
        )

        process_list = ProcessList(
            id="multiple-nodes-process-list",
            compatible_CLF_version="3.0",
            name="Multiple Nodes Process List",
            description=[
                "Test for ProcessList with multiple process nodes XML generation"
            ],
            input_descriptor="Linear",
            output_descriptor="Log",
            process_nodes=[matrix_node, range_node, log_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_process_list_with_exponent_node_xml_generation(self) -> None:
        """
        Test that a ProcessList with an Exponent process node generates valid XML
        according to the schema.
        """
        # Create ExponentParams for each channel
        exponent_params_r = ExponentParams(
            exponent=2.2,
            offset=0.0,
            channel=Channel.R,
        )

        exponent_params_g = ExponentParams(
            exponent=2.4,
            offset=0.05,
            channel=Channel.G,
        )

        exponent_params_b = ExponentParams(
            exponent=2.6,
            offset=0.05,
            channel=Channel.B,
        )

        exponent_node = Exponent(
            id="channel-specific-exponent-test",
            name="Channel-Specific Exponent Test",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            style=ExponentStyle.BASIC_REV,
            description=["Exponent transform with channel-specific parameters"],
            exponent_params=[exponent_params_r, exponent_params_g, exponent_params_b],
        )

        process_list = ProcessList(
            id="exponent-test-process-list",
            compatible_CLF_version="3.0",
            name="Exponent Test Process List",
            description=[
                "Test for Exponent with channel-specific parameters XML generation"
            ],
            input_descriptor="Linear",
            output_descriptor="Gamma",
            process_nodes=[exponent_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_process_list_with_asc_cdl_node_xml_generation(self) -> None:
        """
        Test that a ProcessList with an ASC_CDL process node generates valid XML
        according to the schema.
        """
        sop_node = SOPNode(
            slope=(1.1, 0.9, 1.0),
            offset=(0.05, 0.05, 0.0),
            power=(0.9, 1.1, 1.0),
        )

        sat_node = SatNode(
            saturation=0.8,
        )

        asc_cdl_node = ASC_CDL(
            id="asc-cdl-test",
            name="ASC CDL Test",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            style=ASC_CDLStyle.FWD,
            description=["ASC CDL transform for testing"],
            sopnode=sop_node,
            sat_node=sat_node,
        )

        process_list = ProcessList(
            id="asc-cdl-test-process-list",
            compatible_CLF_version="3.0",
            name="ASC CDL Test Process List",
            description=["Test for ASC_CDL XML generation"],
            input_descriptor="Linear",
            output_descriptor="Linear",
            process_nodes=[asc_cdl_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_process_list_with_lut1d_half_domain_xml_generation(self) -> None:
        """
        Test that a ProcessList with a LUT1D process node using half domain generates
        valid XML according to the schema.
        """
        lut_array = Array(values=[0.0, 0.25, 0.5, 0.75, 1.0], dim=(5, 1))

        lut1d_node = LUT1D(
            id="lut1d-half-domain-test",
            name="1D LUT with Half Domain",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=lut_array,
            description=["1D LUT with half domain for testing"],
            half_domain=True,
            raw_halfs=True,
            interpolation=Interpolation1D.LINEAR,
        )

        process_list = ProcessList(
            id="lut1d-half-domain-test-process-list",
            compatible_CLF_version="3.0",
            name="LUT1D Half Domain Test Process List",
            description=["Test for LUT1D with half domain XML generation"],
            input_descriptor="Linear",
            output_descriptor="Custom",
            process_nodes=[lut1d_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_log_with_channel_specific_params_xml_generation(self) -> None:
        """
        Test that a Log process node with channel-specific parameters generates valid
        XML according to the schema.
        """
        log_params_r = LogParams(
            base=10.0,
            log_side_slope=1.0,
            log_side_offset=0.0,
            lin_side_slope=1.0,
            lin_side_offset=0.0,
            lin_side_break=0.01,
            linear_slope=None,
            channel=Channel.R,
        )

        log_params_g = LogParams(
            base=10.0,
            log_side_slope=0.9,
            log_side_offset=0.05,
            lin_side_slope=1.1,
            lin_side_offset=0.01,
            lin_side_break=0.02,
            linear_slope=None,
            channel=Channel.G,
        )

        log_params_b = LogParams(
            base=10.0,
            log_side_slope=1.1,
            log_side_offset=-0.05,
            lin_side_slope=0.9,
            lin_side_offset=-0.01,
            lin_side_break=0.03,
            linear_slope=None,
            channel=Channel.B,
        )

        log_node = Log(
            id="channel-specific-log-test",
            name="Channel-Specific Log Test",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            style=LogStyle.LOG_10,
            description=["Log10 transform with channel-specific parameters"],
            log_params=[log_params_r, log_params_g, log_params_b],
        )

        process_list = ProcessList(
            id="channel-specific-log-test-process-list",
            compatible_CLF_version="3.0",
            name="Channel-Specific Log Test",
            description=[
                "Test for Log with channel-specific parameters XML generation"
            ],
            input_descriptor="Linear",
            output_descriptor="Log",
            process_nodes=[log_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_lut1d_with_interpolation_xml_generation(self) -> None:
        """
        Test that a LUT1D process node with explicit interpolation method generates
        valid XML according to the schema.
        """
        lut_array = Array(values=[0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0], dim=(7, 1))

        lut1d_node = LUT1D(
            id="lut1d-interpolation-test",
            name="1D LUT with Interpolation",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=lut_array,
            description=["1D LUT with explicit interpolation method"],
            half_domain=False,
            raw_halfs=False,
            interpolation=Interpolation1D.LINEAR,
        )

        process_list = ProcessList(
            id="lut1d-interpolation-test-process-list",
            compatible_CLF_version="3.0",
            name="LUT1D Interpolation Test",
            description=["Test for LUT1D with interpolation XML generation"],
            input_descriptor="Linear",
            output_descriptor="Custom",
            process_nodes=[lut1d_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_range_with_extreme_values_xml_generation(self) -> None:
        """
        Test that a Range process node with extreme values generates valid XML
        according to the schema.
        """
        range_node = Range(
            id="range-extreme-values-test",
            name="Range with Extreme Values",
            in_bit_depth=BitDepth.f32,
            out_bit_depth=BitDepth.f32,
            min_in_value=-1e6,  # Very negative input value
            max_in_value=1e6,  # Very positive input value
            min_out_value=0.0,  # Clamp to standard range
            max_out_value=1.0,
            description=["Range transform with extreme values"],
            style=RangeStyle.CLAMP,
        )

        process_list = ProcessList(
            id="range-extreme-values-test-process-list",
            compatible_CLF_version="3.0",
            name="Range Extreme Values Test",
            description=["Test for Range with extreme values XML generation"],
            input_descriptor="Extended Range",
            output_descriptor="Normalized Range",
            process_nodes=[range_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_lut3d_with_different_interpolation_xml_generation(self) -> None:
        """
        Test that a LUT3D process node with different interpolation methods generates
        valid XML according to the schema.
        """
        lut_array = Array(
            values=[
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                1.0,
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
                0.0,
                0.0,
                1.0,
                0.0,
                1.0,
                1.0,
                1.0,
                0.0,
                1.0,
                1.0,
                1.0,
            ],
            dim=(2, 2, 2, 3),
        )

        lut3d_node = LUT3D(
            id="lut3d-tetrahedral-test",
            name="3D LUT with Tetrahedral Interpolation",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=lut_array,
            interpolation=Interpolation3D.TETRAHEDRAL,
            description=["3D LUT with tetrahedral interpolation"],
            half_domain=False,
            raw_halfs=False,
        )

        process_list = ProcessList(
            id="lut3d-tetrahedral-test-process-list",
            compatible_CLF_version="3.0",
            name="LUT3D Tetrahedral Interpolation Test",
            description=[
                "Test for LUT3D with tetrahedral interpolation XML generation"
            ],
            input_descriptor="RGB",
            output_descriptor="RGB",
            process_nodes=[lut3d_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_mixed_bit_depths_process_list_xml_generation(self) -> None:
        """
        Test that a ProcessList with mixed bit depths between process nodes generates
        valid XML according to the schema.
        """
        matrix_array = Array(
            values=[
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
            ],
            dim=(3, 3),
        )

        matrix_node = Matrix(
            id="matrix-bit-depth-test",
            name="Matrix with Bit Depth Change",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.i10,
            array=matrix_array,
            description=["Identity matrix with bit depth change"],
        )

        range_node = Range(
            id="range-bit-depth-test",
            name="Range with Bit Depth Change",
            in_bit_depth=BitDepth.i10,
            out_bit_depth=BitDepth.f32,
            min_in_value=0.0,
            max_in_value=1023.0,
            min_out_value=0.0,
            max_out_value=1.0,
            description=["Range transform with bit depth change"],
            style=RangeStyle.CLAMP,
        )

        process_list = ProcessList(
            id="mixed-bit-depths-process-list",
            compatible_CLF_version="3.0",
            name="Mixed Bit Depths Process List",
            description=["Test for ProcessList with mixed bit depths XML generation"],
            input_descriptor="Float16",
            output_descriptor="Float32",
            process_nodes=[matrix_node, range_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_matrix_xml_generation(self) -> None:
        """
        Test that a Matrix process node generates valid XML according to the schema.
        """
        matrix_array = Array(
            values=[
                1.45143931614567,
                -0.236510746893740,
                -0.214928569251925,
                -0.0765537733960204,
                1.17622969983357,
                -0.0996759264375522,
                0.00831614842569772,
                -0.00603244979102103,
                0.997716301365324,
            ],
            dim=(3, 3),
        )

        matrix_node = Matrix(
            id="matrix-test",
            name="AP0 to AP1",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=matrix_array,
            description=["3x3 color space conversion from AP0 to AP1"],
        )

        process_list = ProcessList(
            id="matrix-test-process-list",
            compatible_CLF_version="3.0",
            name="Matrix Test",
            description=["Test for Matrix XML generation"],
            input_descriptor="ACES2065-1",
            output_descriptor="ACEScg",
            process_nodes=[matrix_node],
            inverse_of=None,
            info=None,
        )
        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_lut1d_xml_generation(self) -> None:
        """
        Test that a LUT1D process node generates valid XML according to the schema.
        """
        lut_array = Array(values=[0.0, 0.25, 0.5, 0.75, 1.0], dim=(5, 1))

        lut1d_node = LUT1D(
            id="lut1d-test",
            name="Simple 1D LUT",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=lut_array,
            description=["Simple 1D LUT for testing"],
            half_domain=False,
            raw_halfs=False,
            interpolation=None,
        )

        process_list = ProcessList(
            id="lut1d-test-process-list",
            compatible_CLF_version="3.0",
            name="LUT1D Test",
            description=["Test for LUT1D XML generation"],
            input_descriptor="Linear",
            output_descriptor="Custom",
            process_nodes=[lut1d_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_lut3d_xml_generation(self) -> None:
        """
        Test that a LUT3D process node generates valid XML according to the schema.
        """
        lut_array = Array(
            values=[
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                1.0,
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
                0.0,
                0.0,
                1.0,
                0.0,
                1.0,
                1.0,
                1.0,
                0.0,
                1.0,
                1.0,
                1.0,
            ],
            dim=(2, 2, 2, 3),
        )

        lut3d_node = LUT3D(
            id="lut3d-test",
            name="Simple 3D LUT",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=lut_array,
            interpolation=Interpolation3D.TRILINEAR,
            description=["Simple 3D LUT for testing"],
            half_domain=False,
            raw_halfs=False,
        )

        process_list = ProcessList(
            id="lut3d-test-process-list",
            compatible_CLF_version="3.0",
            name="LUT3D Test",
            description=["Test for LUT3D XML generation"],
            input_descriptor="RGB",
            output_descriptor="RGB",
            process_nodes=[lut3d_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_asc_cdl_xml_generation(self) -> None:
        """
        Test that an ASC_CDL process node generates valid XML according to the schema.
        """
        sop_node = SOPNode(
            slope=(1.0, 1.0, 0.9),
            offset=(-0.03, -0.02, 0.0),
            power=(1.25, 1.0, 1.0),
        )

        sat_node = SatNode(saturation=1.7)

        asc_cdl_node = ASC_CDL(
            id="asc-cdl-test",
            name="ASC CDL Test",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            style=ASC_CDLStyle.FWD,
            sopnode=sop_node,
            sat_node=sat_node,
            description=["ASC CDL for testing"],
        )

        process_list = ProcessList(
            id="asc-cdl-test-process-list",
            compatible_CLF_version="3.0",
            name="ASC CDL Test",
            description=["Test for ASC CDL XML generation"],
            input_descriptor="ACES2065-1",
            output_descriptor="ACES2065-1",
            process_nodes=[asc_cdl_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_log_xml_generation(self) -> None:
        """
        Test that a Log process node generates valid XML according to the schema.
        """
        log_params = LogParams(
            base=10.0,
            log_side_slope=1.0,
            log_side_offset=0.0,
            lin_side_slope=1.0,
            lin_side_offset=0.0,
            lin_side_break=None,
            linear_slope=None,
            channel=None,
        )

        log_node = Log(
            id="log-test",
            name="Log Test",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            style=LogStyle.LOG_10,
            description=["Log10 transform for testing"],
            log_params=[log_params],
        )

        process_list = ProcessList(
            id="log-test-process-list",
            compatible_CLF_version="3.0",
            name="Log Test",
            description=["Test for Log XML generation"],
            input_descriptor="Linear",
            output_descriptor="Log",
            process_nodes=[log_node],
            inverse_of=None,
            info=None,
        )
        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_exponent_xml_generation(self) -> None:
        """
        Test that an Exponent process node generates valid XML according to the schema.
        """
        exponent_params = ExponentParams(exponent=2.2, offset=None, channel=None)

        exponent_node = Exponent(
            id="exponent-test",
            name="Exponent Test",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            style=ExponentStyle.BASIC_FWD,
            description=["Basic gamma transform for testing"],
            exponent_params=[exponent_params],
        )

        process_list = ProcessList(
            id="exponent-test-process-list",
            compatible_CLF_version="3.0",
            name="Exponent Test",
            description=["Test for Exponent XML generation"],
            input_descriptor="Linear",
            output_descriptor="Gamma",
            process_nodes=[exponent_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_range_xml_generation(self) -> None:
        """
        Test that a Range process node generates valid XML according to the schema.
        """
        range_node = Range(
            id="range-test",
            name="Range Test",
            in_bit_depth=BitDepth.i10,
            out_bit_depth=BitDepth.i10,
            min_in_value=0.0,
            max_in_value=1023.0,
            min_out_value=64.0,
            max_out_value=940.0,
            description=["Range transform for testing"],
            style=RangeStyle.CLAMP,
        )

        process_list = ProcessList(
            id="range-test-process-list",
            compatible_CLF_version="3.0",
            name="Range Test",
            description=["Test for Range XML generation"],
            input_descriptor="Full Range",
            output_descriptor="Video Range",
            process_nodes=[range_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_complex_process_list_xml_generation(self) -> None:
        """
        Test that a complex ProcessList with multiple nodes generates valid XML
        according to the schema.
        """
        matrix_array = Array(
            values=[
                1.45143931614567,
                -0.236510746893740,
                -0.214928569251925,
                -0.0765537733960204,
                1.17622969983357,
                -0.0996759264375522,
                0.00831614842569772,
                -0.00603244979102103,
                0.997716301365324,
            ],
            dim=(3, 3),
        )

        matrix_node = Matrix(
            id="matrix-node",
            name="AP0 to AP1",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=matrix_array,
            description=["3x3 color space conversion from AP0 to AP1"],
        )

        # Create a log node
        log_params = LogParams(
            base=10.0,
            log_side_slope=1.0,
            log_side_offset=0.0,
            lin_side_slope=1.0,
            lin_side_offset=0.0,
            lin_side_break=None,
            linear_slope=None,
            channel=None,
        )

        log_node = Log(
            id="log-node",
            name="Log Transform",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            style=LogStyle.LOG_10,
            description=["Log10 transform"],
            log_params=[log_params],
        )

        process_list = ProcessList(
            id="complex-process-list",
            compatible_CLF_version="3.0",
            name="Complex Process List",
            description=["Test for complex ProcessList XML generation"],
            input_descriptor="ACES2065-1",
            output_descriptor="Log ACEScg",
            process_nodes=[matrix_node, log_node],
            inverse_of=None,
            info=None,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)

    def test_process_list_with_info_and_calibration_info_xml_generation(self) -> None:
        """
        Test that a ProcessList with Info and CalibrationInfo elements generates valid
        XML according to the schema.
        """
        calibration_info = CalibrationInfo(
            display_device_serial_num="ABC123456",
            display_device_host_name="DisplayHost1",
            operator_name="John Doe",
            calibration_date_time="2023-05-15T14:30:00",
            measurement_probe="Probe Model XYZ",
            calibration_software_name="CalSoftware",
            calibration_software_version="1.2.3",
        )

        info = Info(
            app_release="App v2.0",
            copyright="Copyright 2023 Test Company",
            revision="1.0",
            aces_transform_id="urn:ampas:aces:transformId:v1.5:MyTransform.a1.v1",
            aces_user_name="My ACES Transform",
            calibration_info=calibration_info,
        )

        matrix_array = Array(
            values=[
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
            ],
            dim=(3, 3),
        )

        matrix_node = Matrix(
            id="identity-matrix",
            name="Identity Matrix",
            in_bit_depth=BitDepth.f16,
            out_bit_depth=BitDepth.f16,
            array=matrix_array,
            description=["Identity matrix for testing"],
        )

        process_list = ProcessList(
            id="info-test-process-list",
            compatible_CLF_version="3.0",
            name="Info Test Process List",
            description=[
                "Test for ProcessList with Info and CalibrationInfo XML generation"
            ],
            input_descriptor="RGB",
            output_descriptor="RGB",
            process_nodes=[matrix_node],
            inverse_of=None,
            info=info,
        )

        xml_str = write_clf(process_list, namespace=Namespaces.SMTP)
        assert_valid_schema_schema_smtp_st2136_1(xml_str)
