# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2022 Alexander Hering             *
****************************************************
"""
import uuid


CHART_COLORS = [
"#008080",
"#ff0000",
"#e6e6fa",
"#ffd700",
"#ffa500",
"#00ffff",
"#ff7373",
"#0000ff",
"#faebd7",
"#bada55",
"#003366",
"#fa8072",
"#ffff00",
"#ffb6c1",
"#c0c0c0",
"#8a2be2",
"#dddddd",
"#0a75ad",
"#2acaea",
"#ff4040",
"#66cccc",
"#420420"
]


"""
 
            var 3995dae9-7c4b-45d5-b9dc-c8f47bfdd2ea = {{'labels': ['testA', 'testB', 'testC'], 'datasets': [{'label': '3995dae9-7c4b-45d5-b9dc-c8f47bfdd2ea', 'data': [1, 2, 3], 'spanGaps': false, 'backgroundColor': ['#008080', '#ff0000', '#e6e6fa']}]}}
               // get chart canvas
               var ctx = document.getElementById("f7c8e90d-ad16-4d0d-b079-4f9a39b39df8").getContext("2d");
               // create the chart using the chart canvas
               var myChart = new Chart(ctx, {{'type': 'pie', 'data': '3995dae9-7c4b-45d5-b9dc-c8f47bfdd2ea', 'options': {'title': {'display': true, 'text': 'My Chart'}}}});
         
"""



class ChartController(object):
    """
    ChartController class for managing charts.
    """
    def __init__(self) -> None:
        """
        Initiation method for ChartController objects.
        """
        self.charts = {}

    def add_chart_script(self, script: str) -> str:
        """
        Method for adding full chart scripts.
        :param script: Chart Javascript code.
        :return: Chart UUID.
        """
        current_uuid = str(uuid.uuid4()).replace("-", "")
        self.charts[current_uuid] = script
        return current_uuid

    def create_pie_chart(self, title: str, labels: list, data: list, colors: list = None, hover_colors: list = None, border_width: list = None, chart_type: str = "pie") -> str:
        """
        Method for creating pie-charrt.
        :param title: Chart title.
        :param labels: Dataset labels.
        :param data: Data points.
        :param colors: Colors in the order of data points. Defaults to standard colors.
        :param hover_colors: Hovering colors in the order of data points. Defaults to standard colors.
        :param border_width: Border widths in order of data points.
        :param chart_type: Chart type, choosable from 'pie', 'doughnut' or 'polarArea'. Defaults to 'pie'.
        :return: UUID for javascript representing the Chart.js-chart. Acquire chart via ChartController.charts[<uuid>].
        """
        if colors is None:
            colors = CHART_COLORS[:len(data)]
        current_uuid = str(uuid.uuid4()).replace("-", "")
        script = f"""
            var d{current_uuid} = {{
                labels: {str(labels)},
                datasets: [{{
                    label: '{current_uuid}',
                    data: {str(data)},
                        spanGaps: false,
                        backgroundColor: {str(colors)},
        """
        if hover_colors is not None:
            script += f"                hoverBackgroundColor: {str(hover_colors)},"
        if border_width is not None:
            script += f"                borderWidth: {str(border_width)},"
        script += f"""
                }}]
            }}
        """

        script += f"""
                // get chart canvas
                var ctx = document.getElementById("{current_uuid}").getContext("2d");
                // create the chart using the chart canvas
                var c{current_uuid} = new Chart(ctx, {{
                    type: '{chart_type}',
                    data: d{current_uuid},
                    options: {{
                        title: {{
                            display: true,
                            text: '{title}',
                        }}
                    }}
                }});
        """
        self.charts[current_uuid] = script
        return current_uuid

    def create_bar_chart(self, title: str, labels: list, data: list, colors: list = None, hover_colors: list = None, border_width: list = None, doughnut: bool = False) -> str:
        """
        Method for creating bar-chart.
        :return: UUID for javascript representing the Chart.js-chart. Acquire chart via ChartController.charts[<uuid>].
        """
        current_uuid = str(uuid.uuid4()).replace("-", "")
        #TODO: Implement
        raise NotImplementedError("Dedicated method is not implemented yet, please create script externally and add via 'add_chart_script'-method.")
        script = f"""
        """
        self.charts[current_uuid] = script
        return current_uuid

    def create_line_chart(self, title: str, labels: list, data: list, colors: list = None, hover_colors: list = None, border_width: list = None, doughnut: bool = False) -> str:
        """
        Method for creating line-chart.
        :return: UUID for javascript representing the Chart.js-chart. Acquire chart via ChartController.charts[<uuid>].
        """
        current_uuid = str(uuid.uuid4()).replace("-", "")
        #TODO: Implement
        raise NotImplementedError(
            "Dedicated method is not implemented yet, please create script externally and add via 'add_chart_script'-method.")
        script = f"""
        """
        self.charts[current_uuid] = script
        return current_uuid

    def create_radar_chart(self, title: str, labels: list, data: list, colors: list = None, hover_colors: list = None, border_width: list = None, doughnut: bool = False) -> str:
        """
        Method for creating radar-chart.
        :return: UUID for javascript representing the Chart.js-chart. Acquire chart via ChartController.charts[<uuid>].
        """
        current_uuid = str(uuid.uuid4()).replace("-", "")
        #TODO: Implement
        raise NotImplementedError(
            "Dedicated method is not implemented yet, please create script externally and add via 'add_chart_script'-method.")
        script = f"""
        """
        self.charts[current_uuid] = script
        return current_uuid

    def get_chart_script(self, chart: str) -> str:
        """
        Method for acquiring chart script.
        :param chart: Chart UUID.
        :return: Chart script to be rendered inside '<script></script>' tags.
        """
        return self.charts[chart]

    def get_chart_element(self, chart: str) -> str:
        """
        Method for acquiring chart element.
        :param chart: Chart UUID.
        :return: Chart element to be rendered inside '<html></html>' tags.
        """
        return f"""
        <canvas id="{chart}" width="1200" height="600" style="display: block; height: 300px; width: 600px;"></canvas>
        """
