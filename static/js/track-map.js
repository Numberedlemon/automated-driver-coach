
    // this does work, jinja is just weird.
    const data = {{data|safe}};

    // get domain sizes by hand because json is weird
    const xval = Object.values(data.Latitude)
    const yval = Object.values(data.Longitude)
    const zval = Object.values(data.Velocity)
    const timeval = Object.values(data.Time)

    const combinedData = [];

    // put x and y values into array again...
    for (let i = 0; i < xval.length; i++) {

        combinedData.push({ x: xval[i], y: yval[i], z: zval[i], time: timeval[i]});
    }

    function createTrackMap(data) {

        // set margins
        const width = 500;
        const height = 500;
        const margin = {top: 20, right: 30, bottom: 40, left: 50};

        // make svg and append
        const svg = d3.select("#chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const x = d3.scaleLinear()
            .domain(d3.extent(data, d => d.x))
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain(d3.extent(data, d => d.y))
            .range([height, 0]);

        const colorScale = d3.scaleSequential()
            .domain(d3.extent(data, d => d.z))
            .interpolator(d3.interpolateViridis);

        const xAxis = svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x));

        const yAxis = svg.append("g")
            .call(d3.axisLeft(y));

        svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "end")
        .attr("x", width - margin.right + 20)
        .attr("y", height + margin.bottom - 5)
        .text("Latitude (deg W)");

        // Add Y axis label
        svg.append("text")
            .attr("class", "y label")
            .attr("text-anchor", "end")
            .attr("y", -margin.left)
            .attr("x", -margin.top)
            .attr("dy", ".75em")
            .attr("transform", "rotate(-90)")
            .text("Longitude (deg N)");

        const updateChart = () => {
            const circles = svg.selectAll(".circle")
                .data(data);

            circles.enter().append("circle")
                .attr("class", "circle")
                .attr("cx", d => x(d.x))
                .attr("cy", d => y(d.y))
                .attr("r", 5)
                .style("fill", (d) => colorScale(d.z))
                .style("opacity", 0)
                .transition()
                .duration(500)
                .delay((d, i) => i * 2) // Cascading delay for each circle
                .style("opacity", 1);

            circles.exit().remove();
        };

        updateChart();
    }

    createTrackMap(combinedData);

    function createVelocityTrace(data) {
        
        // set margins
        const width = 500;
        const height = 500;
        const margin = {top: 20, right: 30, bottom: 40, left: 50};

        // make svg and append
        const svg = d3.select("#chart2").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const x = d3.scaleLinear()
            .domain(d3.extent(data, d => d.time))
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain(d3.extent(data, d => d.z))
            .range([height, 0]);

        const xAxis = svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x));

        const yAxis = svg.append("g")
            .call(d3.axisLeft(y));

        svg.append("text")
            .attr("class", "x label")
            .attr("text-anchor", "end")
            .attr("x", width - margin.right + 20)
            .attr("y", height + margin.bottom - 5)
            .text("Time (s)");

        // Add Y axis label
        svg.append("text")
            .attr("class", "y label")
            .attr("text-anchor", "end")
            .attr("y", -margin.left)
            .attr("x", -margin.top)
            .attr("dy", ".75em")
            .attr("transform", "rotate(-90)")
            .text("Velocity (kph)");

        const updateChart = () => {

        // Line generator
        const line = d3.line()
            .x(d => x(d.time))
            .y(d => y(d.z));

        // Calculate transition duration based on number of points
        const transitionDuration = data.length * 2; // Adjust the constant factor as needed

        // Draw line with delay
        svg.append("path")
            .datum(data)
            .attr("class", "line")
            .attr("d", line)
            .attr("stroke-dasharray", function() { return this.getTotalLength() })
            .attr("stroke-dashoffset", function() { return this.getTotalLength() })
            .transition()
            .duration(transitionDuration) // Dynamic duration based on data length
            .ease(d3.easeLinear)
            .attr("stroke-dashoffset", 0);
            };

        updateChart();
    }

    createVelocityTrace(combinedData)