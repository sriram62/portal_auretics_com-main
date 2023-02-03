'use strict';
$(document).ready(function() {
    setTimeout(function() {
        floatchart()
    }, 100);
});

function floatchart() {
    // [ realtime-visit-chart ] start
    $(function() {
        var lastDate = 0;
        var data = [];

        function getDayWiseTimeSeries(baseval, count, yrange) {
            var i = 0;
            while (i < count) {
                var x = baseval;
                var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;

                data.push({
                    x,
                    y
                });
                lastDate = baseval
                baseval += 86400000;
                i++;
            }
        }
        getDayWiseTimeSeries(new Date('11 Feb 2017 GMT').getTime(), 10, {
            min: 10,
            max: 90
        })

        function getNewSeries(baseval, yrange) {
            var newDate = baseval + 86400000;
            lastDate = newDate
            data.push({
                x: newDate,
                y: Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min
            })
        }

        function resetData() {
            data = data.slice(data.length - 10, data.length);
        }
        var options = {
            chart: {
                height: 290,
                type: 'area',
                animations: {
                    enabled: true,
                    easing: 'linear',
                    dynamicAnimation: {
                        speed: 2000
                    }
                },
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                }
            },
            dataLabels: {
                enabled: false
            },
            stroke: {
                curve: 'smooth'
            },
            series: [{
                name: 'active Users :',
                data: data
            }],
            colors: ["#e74c3c"],
            fill: {
                type: 'solid',
                opacity: 0,
            },
            markers: {
                size: 0
            },
            xaxis: {
                type: 'datetime',
                range: 777600000,
            },
            yaxis: {
                max: 100
            },
            legend: {
                show: false
            },
        }
        var chart = new ApexCharts(
            document.querySelector("#realtime-visit-chart"),
            options
        );
        chart.render();
        var dataPointsLength = 10;
        window.setInterval(function() {
            getNewSeries(lastDate, {
                min: 10,
                max: 90
            })

            chart.updateSeries([{
                data: data
            }])
        }, 2000)
        window.setInterval(function() {
            resetData()
            chart.updateSeries([{
                data
            }], false, true)
        }, 60000)
    });
    // [ realtime-visit-chart ] end
    // [ seo-anlytics51 ] start
    $(function() {
        var options = {
            chart: {
                type: 'area',
                height: 35,
                sparkline: {
                    enabled: true
                }
            },
            dataLabels: {
                enabled: false
            },
            colors: ["#0073aa"],
            fill: {
                type: 'solid',
                opacity: 0,
            },
            grid: {
                padding: {
                    left: 5,
                    right: 5
                }
            },
            markers: {
                size: 3,
                opacity: 0.9,
                colors: "#0073aa",
                strokeColor: "#0073aa",
                strokeWidth: 1,
                hover: {
                    size: 4,
                }
            },
            stroke: {
                curve: 'straight',
                width: 2,
            },
            series: [{
                name: 'series1',
                data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54, 25, 66, 41, 89]
            }],
            tooltip: {
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function(seriesName) {
                            return 'Site Analysis :'
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        };
        var chart = new ApexCharts(document.querySelector("#seo-anlytics51"), options);
        chart.render();
    });
    // [ seo-anlytics51 ] end
    // [ traffic-chart1 ] start
    $(function() {
        var options = {
            chart: {
                height: 250,
                type: 'donut',
            },
            dataLabels: {
                enabled: true,
                dropShadow: {
                    enabled: false,
                }
            },
            series: [85.7, 77.56, 20.9, 10.9, 15.8, 86.7],
            colors: ["#0073aa", "#0e9e4a", "#00acc1", "#f1c40f", "#e74c3c", "#536dfe"],
            labels: ["Facebook ads", "Amazon ads", "Youtube videos", "Google adsense", "Twitter ads", "News ads"],
            legend: {
                show: true,
                position: 'bottom',
            }
        }
        var chart = new ApexCharts(
            document.querySelector("#traffic-chart1"),
            options
        );
        chart.render();
    });
    // [ traffic-chart1 ] end
    // [ seo-chart1 ] start
    $(function() {
        var options = {
            chart: {
                type: 'area',
                height: 40,
                sparkline: {
                    enabled: true
                }
            },
            dataLabels: {
                enabled: false
            },
            colors: ["#0073aa"],
            fill: {
                type: 'solid',
                opacity: 0.3,
            },
            markers: {
                size: 2,
                opacity: 0.9,
                colors: "#0073aa",
                strokeColor: "#0073aa",
                strokeWidth: 2,
                hover: {
                    size: 4,
                }
            },
            stroke: {
                curve: 'straight',
                width: 3,
            },
            series: [{
                name: 'series1',
                data: [9, 66, 41, 89, 63, 25, 44, 12, 36, 20, 54, 25, 9]
            }],
            tooltip: {
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function(seriesName) {
                            return 'Visits :'
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        };
        var chart = new ApexCharts(document.querySelector("#seo-chart1"), options);
        chart.render();
    });
    // [ seo-chart1 ] end
    // [ seo-chart2 ] start
    $(function() {
        var options = {
            chart: {
                type: 'bar',
                height: 40,
                sparkline: {
                    enabled: true
                }
            },
            dataLabels: {
                enabled: false
            },
            colors: ["#2ecc71"],
            plotOptions: {
                bar: {
                    columnWidth: '60%'
                }
            },
            series: [{
                data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54, 25, 66, 41, 89, 63]
            }],
            xaxis: {
                crosshairs: {
                    width: 1
                },
            },
            tooltip: {
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function(seriesName) {
                            return 'Bounce Rate :'
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        };
        var chart = new ApexCharts(document.querySelector("#seo-chart2"), options);
        chart.render();
    });
    // [ seo-chart2 ] end
    // [ seo-chart3 ] start
    $(function() {
        var options = {
            chart: {
                type: 'area',
                height: 40,
                sparkline: {
                    enabled: true
                }
            },
            dataLabels: {
                enabled: false
            },
            colors: ["#e74c3c"],
            fill: {
                type: 'solid',
                opacity: 0,
            },
            markers: {
                size: 2,
                opacity: 0.9,
                colors: "#e74c3c",
                strokeColor: "#e74c3c",
                strokeWidth: 2,
                hover: {
                    size: 4,
                }
            },
            stroke: {
                curve: 'straight',
                width: 3,
            },
            series: [{
                name: 'series1',
                data: [9, 66, 41, 89, 63, 25, 44, 12, 36, 20, 54, 25, 9]
            }],
            tooltip: {
                fixed: {
                    enabled: false
                },
                x: {
                    show: false
                },
                y: {
                    title: {
                        formatter: function(seriesName) {
                            return 'Products :'
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        };
        var chart = new ApexCharts(document.querySelector("#seo-chart3"), options);
        chart.render();
    });
    // [ seo-chart3 ] end
}
