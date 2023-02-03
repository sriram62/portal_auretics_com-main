'use strict';
$(document).ready(function() {
    // [ session-scroll ] start
    var px = new PerfectScrollbar('.pro-scroll', {
        wheelSpeed: .5,
        swipeEasing: 0,
        wheelPropagation: 1,
        minScrollbarLength: 40,
    });
    // [ session-scroll ] end
    setTimeout(function() {
        floatchart()
    }, 100);
});

function floatchart() {
    // [ seo-ecommerce-barchart ] start
    $(function() {
        var options = {
            chart: {
                type: 'bar',
                height: 200,
                zoom: {
                    enabled: false
                },
                toolbar: {
                    show: false,
                },
            },
            dataLabels: {
                enabled: false,
            },
            colors: ["#0073aa", "#ccc"],
            plotOptions: {
                bar: {
                    color: ['#0073aa', "#ccc"],
                    columnWidth: '60%',
                }
            },
            fill: {
                type: 'solid',
            },
            series: [{
                name: 'Real-Time Visits',
                data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54, 25, 66, 41, 89, 63, 54, 25, 66]
            }, {
                name: 'Returning Visitors',
                data: [25, 36, 9, 54, 25, 66, 41, 89, 63, 44, 12, 89, 63, 25, 44, 12, 54, 25, 66]
            }],
            xaxis: {
                crosshairs: {
                    width: 1
                },
                labels: {
                    show: false,
                },
            },
            grid: {
                borderColor: '#e2e5e829',
                padding: {
                    bottom: 0,
                    left: 10,
                }
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
                            return 'Active Users :'
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        };
        var chart = new ApexCharts(document.querySelector("#seo-ecommerce-barchart"), options);
        chart.render();
    });
    // [ seo-ecommerce-barchart ] end
    // [ seo-chart2 ] start
    $(function() {
        var options = {
            chart: {
                type: 'bar',
                height: 60,
                sparkline: {
                    enabled: true
                }
            },
            dataLabels: {
                enabled: false,
            },
            colors: ["#fff"],
            fill: {
                type: 'solid',
                opacity: 0.5,
            },
            plotOptions: {
                bar: {
                    columnWidth: '50%'
                }
            },
            series: [{
                data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9]
            }],
            xaxis: {
                crosshairs: {
                    width: 1
                },
            },
            tooltip: {
                theme: 'dark',
                fixed: {
                    enabled: false
                },
                x: {
                    show: false,
                },
                y: {
                    title: {
                        formatter: function(seriesName) {
                            return 'Orders'
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        };
        var chart = new ApexCharts(document.querySelector("#resource-barchart1"), options);
        chart.render();
    });
    $(function() {
        var options = {
            chart: {
                type: 'bar',
                height: 60,
                sparkline: {
                    enabled: true
                }
            },
            dataLabels: {
                enabled: false,
            },
            colors: ["#fff"],
            fill: {
                type: 'solid',
                opacity: 0.5,
            },
            plotOptions: {
                bar: {
                    columnWidth: '50%'
                }
            },
            series: [{
                data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9]
            }],
            xaxis: {
                crosshairs: {
                    width: 1
                },
            },
            tooltip: {
                theme: 'dark',
                fixed: {
                    enabled: false
                },
                x: {
                    show: false,
                },
                y: {
                    title: {
                        formatter: function(seriesName) {
                            return 'Orders'
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        };
        var chart = new ApexCharts(document.querySelector("#resource-barchart3"), options);
        chart.render();
    });
    $(function() {
        var options = {
            chart: {
                type: 'bar',
                height: 60,
                sparkline: {
                    enabled: true
                }
            },
            dataLabels: {
                enabled: false,
            },
            colors: ["#fff"],
            fill: {
                type: 'solid',
                opacity: 0.5,
            },
            plotOptions: {
                bar: {
                    columnWidth: '50%'
                }
            },
            series: [{
                data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9]
            }],
            xaxis: {
                crosshairs: {
                    width: 1
                },
            },
            tooltip: {
                theme: 'dark',
                fixed: {
                    enabled: false
                },
                x: {
                    show: false,
                },
                y: {
                    title: {
                        formatter: function(seriesName) {
                            return 'Orders'
                        }
                    }
                },
                marker: {
                    show: false
                }
            }
        };
        var chart = new ApexCharts(document.querySelector("#resource-barchart4"), options);
        chart.render();
    });
    // [ seo-chart2 ] end
}
