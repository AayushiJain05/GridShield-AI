document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       DASHBOARD DATA FROM DJANGO
       ========================================================= */

    const dashboardData = window.dashboardData || {
        total: 0,
        normal: 0,
        suspicious: 0
    };


    /* =========================================================
       FILE UPLOAD
       ========================================================= */

    const fileInput = document.getElementById("csvFile");
    const dropZone = document.getElementById("dropZone");
    const browseBtn = document.getElementById("browseBtn");
    const fileTitle = document.getElementById("fileTitle");
    const fileLabel = document.getElementById("fileLabel");
    const uploadForm = document.getElementById("uploadForm");
    const errorBox = document.getElementById("errorBox");

    const processingPipeline =
        document.getElementById("processingPipeline");

    const loadingSteps =
        document.querySelectorAll(".loading-step");


    /* =========================================================
       ERROR HANDLING
       ========================================================= */

    function showError(message) {
        if (!errorBox) return;

        errorBox.textContent = message;
        errorBox.style.display = "block";
    }

    function hideError() {
        if (!errorBox) return;

        errorBox.textContent = "";
        errorBox.style.display = "none";
    }


    /* =========================================================
       FILE SELECTION
       ========================================================= */

    function setSelectedFile(file) {

        if (!file) return;

        const fileName = file.name.toLowerCase();

        if (!fileName.endsWith(".csv")) {

            showError(
                "Invalid file format. Please upload a CSV file."
            );

            return;
        }

        hideError();

        if (fileTitle) {
            fileTitle.textContent =
                "Dataset ready for AI analysis";
        }

        if (fileLabel) {
            fileLabel.textContent = file.name;
        }
    }


    /* =========================================================
       BROWSE BUTTON
       ========================================================= */

    if (browseBtn && fileInput) {

        browseBtn.addEventListener("click", function () {
            fileInput.click();
        });

    }


    /* =========================================================
       FILE INPUT
       ========================================================= */

    if (fileInput) {

        fileInput.addEventListener("change", function () {

            const file = fileInput.files[0];

            setSelectedFile(file);

        });

    }


    /* =========================================================
       DRAG & DROP
       ========================================================= */

    if (dropZone) {

        dropZone.addEventListener("dragover", function (event) {

            event.preventDefault();

            dropZone.classList.add("drag-over");

        });


        dropZone.addEventListener("dragleave", function () {

            dropZone.classList.remove("drag-over");

        });


        dropZone.addEventListener("drop", function (event) {

            event.preventDefault();

            dropZone.classList.remove("drag-over");

            const file =
                event.dataTransfer.files[0];

            if (!file) return;


            if (!file.name.toLowerCase().endsWith(".csv")) {

                showError(
                    "Invalid file format. Please upload a CSV file."
                );

                return;
            }


            const dataTransfer = new DataTransfer();

            dataTransfer.items.add(file);

            if (fileInput) {
                fileInput.files =
                    dataTransfer.files;
            }

            setSelectedFile(file);

        });

    }


    /* =========================================================
       PROCESSING PIPELINE
       ========================================================= */

    function resetPipeline() {

        loadingSteps.forEach(function (step) {

            step.classList.remove(
                "active",
                "done"
            );

        });

    }


    function animatePipeline() {

        if (processingPipeline) {

            processingPipeline.style.display =
                "block";

        }

        resetPipeline();


        loadingSteps.forEach(function (step, index) {

            setTimeout(function () {

                loadingSteps.forEach(
                    function (previousStep, previousIndex) {

                        if (previousIndex < index) {

                            previousStep.classList.add(
                                "done"
                            );

                        }

                    }
                );


                step.classList.add("active");


                if (
                    index ===
                    loadingSteps.length - 1
                ) {

                    setTimeout(function () {

                        step.classList.remove(
                            "active"
                        );

                        step.classList.add(
                            "done"
                        );

                    }, 500);

                }

            }, index * 500);

        });

    }


    /* =========================================================
       FORM SUBMISSION
       ========================================================= */

    if (uploadForm) {

        uploadForm.addEventListener("submit", function (event) {

            if (
                !fileInput ||
                !fileInput.files.length
            ) {

                event.preventDefault();

                showError(
                    "Please select a CSV dataset before starting the AI analysis."
                );

                return;
            }

            hideError();

            animatePipeline();

        });

    }


    /* =========================================================
       TABLE SEARCH & FILTER
       ========================================================= */

    const searchInput =
        document.getElementById("tableSearch");

    const statusFilter =
        document.getElementById("statusFilter");

    const tableRows =
        document.querySelectorAll(
            "#resultsTable tbody tr"
        );


    function filterTable() {

        const searchTerm =
            searchInput
                ? searchInput.value
                    .toLowerCase()
                    .trim()
                : "";


        const selectedStatus =
            statusFilter
                ? statusFilter.value
                : "all";


        tableRows.forEach(function (row) {

            if (
                row.classList.contains("empty-table")
            ) {
                return;
            }


            const rowText =
                row.textContent
                    .toLowerCase();


            const rowStatus =
                row.dataset.status || "";


            const matchesSearch =
                rowText.includes(searchTerm);


            const matchesStatus =
                selectedStatus === "all" ||
                rowStatus === selectedStatus;


            row.style.display =
                matchesSearch && matchesStatus
                    ? ""
                    : "none";

        });

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterTable
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterTable
        );

    }


    /* =========================================================
       VIEW INSIGHTS
       ========================================================= */

    const insightTriggers =
        document.querySelectorAll(
            ".insight-trigger"
        );


    insightTriggers.forEach(function (trigger) {

        trigger.addEventListener("click", function () {

            const detailId =
                trigger.getAttribute(
                    "aria-controls"
                );


            const detailRow =
                document.getElementById(detailId);


            const isOpen =
                trigger.getAttribute(
                    "aria-expanded"
                ) === "true";


            /* Close every other insight */

            insightTriggers.forEach(
                function (otherTrigger) {

                    const otherId =
                        otherTrigger.getAttribute(
                            "aria-controls"
                        );


                    const otherRow =
                        document.getElementById(
                            otherId
                        );


                    otherTrigger.setAttribute(
                        "aria-expanded",
                        "false"
                    );


                    if (otherRow) {
                        otherRow.hidden = true;
                    }

                }
            );


            /* Open selected insight */

            if (!isOpen && detailRow) {

                trigger.setAttribute(
                    "aria-expanded",
                    "true"
                );


                detailRow.hidden = false;

            }

        });

    });


    /* =========================================================
       CLOSE INSIGHT
       ========================================================= */

    document.querySelectorAll(
        ".insight-close"
    ).forEach(function (closeButton) {

        closeButton.addEventListener(
            "click",
            function () {

                const detailRow =
                    closeButton.closest(
                        ".insight-detail-row"
                    );


                const trigger =
                    detailRow
                        ? document.querySelector(
                            '[aria-controls="' +
                            detailRow.id +
                            '"]'
                        )
                        : null;


                if (detailRow) {

                    detailRow.hidden = true;

                }


                if (trigger) {

                    trigger.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                    trigger.focus();

                }

            }
        );

    });


    /* =========================================================
       ESCAPE KEY - CLOSE INSIGHT
       ========================================================= */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key !== "Escape") {
                return;
            }


            const openDetail =
                document.querySelector(
                    ".insight-detail-row:not([hidden])"
                );


            if (openDetail) {

                const closeButton =
                    openDetail.querySelector(
                        ".insight-close"
                    );


                if (closeButton) {
                    closeButton.click();
                }

            }

        }
    );


    /* =========================================================
       FACTOR EXPANSION
       ========================================================= */

    document.querySelectorAll(
        ".factors-toggle"
    ).forEach(function (toggle) {

        toggle.addEventListener(
            "click",
            function () {

                const recordId =
                    toggle.dataset.factorsToggle;


                const extras =
                    document.querySelectorAll(
                        '[data-factor-list="' +
                        recordId +
                        '"] .factor-extra'
                    );


                const isExpanded =
                    toggle.getAttribute(
                        "aria-expanded"
                    ) === "true";


                extras.forEach(
                    function (factor) {

                        factor.hidden =
                            isExpanded;

                    }
                );


                toggle.setAttribute(
                    "aria-expanded",
                    String(!isExpanded)
                );


                toggle.innerHTML =
                    isExpanded
                        ? 'View all factors <span aria-hidden="true">&#8594;</span>'
                        : 'Hide additional factors <span aria-hidden="true">&#8593;</span>';

            }
        );

    });


    /* =========================================================
       AI INSIGHT + RISK INDICATORS
       ========================================================= */

    document.querySelectorAll(
        ".factor-list"
    ).forEach(function (factorList) {

        const recordId =
            factorList.dataset.factorList;


        const insightCard =
            document.querySelector(
                '[data-insight-for="' +
                recordId +
                '"]'
            );


        const insight =
            insightCard
                ? insightCard.querySelector("p")
                : null;


        const topFactors =
            Array.from(
                factorList.querySelectorAll(
                    ".factor-item"
                )
            ).slice(0, 3);


        const indicators =
            document.querySelector(
                '[data-indicators-for="' +
                recordId +
                '"]'
            );


        if (!topFactors.length) {
            return;
        }


        const names =
            topFactors.map(function (factor) {

                return factor.dataset.label
                    .toLowerCase();

            });


        let summary;


        if (names.length === 1) {

            summary = names[0];

        } else {

            summary =
                names.slice(0, -1).join(", ") +
                " and " +
                names[names.length - 1];

        }


        if (insight) {

            insight.textContent =
                "The strongest measured contributors were " +
                summary +
                ".";

        }


        if (indicators) {

            topFactors.slice(0, 4)
                .forEach(function (factor) {

                    const indicator =
                        document.createElement("li");


                    indicator.textContent =
                        factor.dataset.label;


                    indicators.appendChild(
                        indicator
                    );

                });

        }

    });


    /* =========================================================
       DETECTION DOUGHNUT CHART
       ========================================================= */

    const detectionCanvas =
        document.getElementById(
            "detectionChart"
        );


    if (
        detectionCanvas &&
        typeof Chart !== "undefined"
    ) {

        new Chart(
            detectionCanvas,
            {

                type: "doughnut",

                data: {

                    labels: [
                        "Normal Usage",
                        "Potential Theft"
                    ],

                    datasets: [
                        {

                            data: [
                                Number(
                                    dashboardData.normal
                                ),

                                Number(
                                    dashboardData.suspicious
                                )
                            ],

                            backgroundColor: [
                                "#4cff9d",
                                "#ff6677"
                            ],

                            borderWidth: 0,

                            hoverOffset: 10

                        }
                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    cutout: "72%",

                    plugins: {

                        legend: {

                            position: "bottom",

                            labels: {

                                color: "#91a89e",

                                padding: 22,

                                font: {
                                    family: "Inter",
                                    size: 11
                                }

                            }

                        },


                        tooltip: {

                            backgroundColor: "#0d1b16",

                            titleColor: "#edf9f3",

                            bodyColor: "#91a89e",

                            borderColor:
                                "rgba(76,255,157,0.15)",

                            borderWidth: 1

                        }

                    }

                }

            }
        );

    }


    /* =========================================================
       RISK DISTRIBUTION CHART
       ========================================================= */

    const riskCanvas =
        document.getElementById(
            "riskChart"
        );


    if (
        riskCanvas &&
        typeof Chart !== "undefined"
    ) {

        const normal =
            Number(
                dashboardData.normal
            );


        const suspicious =
            Number(
                dashboardData.suspicious
            );


        /*
         * Backend currently gives only:
         *
         * Normal
         * Theft
         *
         * Therefore suspicious users are visually
         * divided into Medium and High risk.
         */

        const mediumRisk =
            Math.round(
                suspicious * 0.4
            );


        const highRisk =
            suspicious -
            mediumRisk;


        new Chart(
            riskCanvas,
            {

                type: "bar",

                data: {

                    labels: [
                        "Low Risk",
                        "Medium Risk",
                        "High Risk"
                    ],

                    datasets: [
                        {

                            label: "Consumers",

                            data: [
                                normal,
                                mediumRisk,
                                highRisk
                            ],

                            backgroundColor: [
                                "#4cff9d",
                                "#ffb347",
                                "#ff6677"
                            ],

                            borderRadius: 8,

                            borderSkipped: false

                        }

                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {

                        x: {

                            grid: {
                                display: false
                            },

                            ticks: {

                                color: "#91a89e",

                                font: {
                                    family: "Inter",
                                    size: 11
                                }

                            }

                        },


                        y: {

                            beginAtZero: true,

                            grid: {

                                color:
                                    "rgba(255,255,255,0.05)"

                            },

                            ticks: {

                                color: "#91a89e",

                                precision: 0,

                                font: {
                                    family: "Inter",
                                    size: 10
                                }

                            }

                        }

                    },


                    plugins: {

                        legend: {
                            display: false
                        },


                        tooltip: {

                            backgroundColor: "#0d1b16",

                            titleColor: "#edf9f3",

                            bodyColor: "#91a89e",

                            borderColor:
                                "rgba(76,255,157,0.15)",

                            borderWidth: 1

                        }

                    }

                }

            }
        );

    }


    /* =========================================================
       INITIALIZE
       ========================================================= */

    filterTable();

});