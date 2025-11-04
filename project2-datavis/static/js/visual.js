window.onload = function() {
    const width = window.innerWidth;
    const height = window.innerHeight;

    const svg = d3.select('#visualization')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('background', '#000');

    if (!listeningData || listeningData.length === 0) {
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', height / 2)
            .attr('text-anchor', 'middle')
            .attr('fill', '#fff')
            .attr('font-size', '20px')
            .text('No listening data available');
        return;
    }

    // filter tracks with audio features
    const tracks = listeningData.filter(t => t.audio_features);

    // polygon layer
    const polygonsGroup = svg.append('g').attr('class', 'polygons');
    
    tracks.forEach((track, i) => { 
        const af = track.audio_features;
        const progress = i / tracks.length;
        const sides = Math.floor(3 + af.instrumentalness * 12);
        const size = af.loudness * -5 + 100;
        const x = width * progress;
        const y = height * af.danceability;

        const points = d3.range(sides).map(j => { 
            const angle = (j / sides) * Math.PI * 2 + af.valence * Math.PI * 2; // rotate based on valence
            const px = x + Math.cos(angle) * size * af.energy; // radius based on energy
            const py = y + Math.sin(angle) * size * af.acousticness; // radius based on acousticness
            return [px, py];
        });

        polygonsGroup.append('polygon')
            .attr('points', points.map(p => p.join(',')).join(' '))
            .attr('fill', `hsla(${af.speechiness * 360}, 80%, 60%, ${af.liveness * 0.3})`) // color based on speechiness and liveness
            .attr('stroke', 'none');
    });

    // vertical stripes layer
    const bandsGroup = svg.append('g').attr('class', 'bands');
    const bandWidth = width / tracks.length;

    tracks.forEach((track, i) => {
        const af = track.audio_features;
        const xPos = i * bandWidth;

        d3.range(0, height, 5).forEach(y => {
            const intensity = Math.sin((y / height) * Math.PI * af.tempo / 50) * af.energy; // wave effect based on tempo and energy
            bandsGroup.append('rect')
                .attr('x', xPos)
                .attr('y', y)
                .attr('width', bandWidth)
                .attr('height', 5)
                .attr('fill', `hsla(${(af.danceability + y / height) * 360}, ${af.valence * 100}%, ${50 + intensity * 30}%, ${af.instrumentalness * 0.4})`); // color based on danceability and valence
        });
    });

    // funky circles layer
    const circlesGroup = svg.append('g').attr('class', 'circles');

    tracks.forEach((track, i) => {
        const af = track.audio_features;
        const progress = i / tracks.length;
        const numCircles = Math.floor(10 + af.speechiness * 20);
        const cx = width * (af.acousticness * 0.5 + 0.25);
        const cy = height * (af.liveness * 0.5 + 0.25 + progress * 0.5);

        d3.range(numCircles).forEach(j => {
            const circleProgress = j / numCircles;
            const r = circleProgress * af.energy * 300;

            circlesGroup.append('circle')
                .attr('cx', cx)
                .attr('cy', cy)
                .attr('r', r)
                .attr('fill', 'none')
                .attr('stroke', `hsla(${(af.valence + circleProgress) * 360}, 70%, 60%, ${(1 - circleProgress) * af.danceability * 0.2})`) // color based on valence and danceability
                .attr('stroke-width', af.loudness * -0.5 + 10);
        });
    });


    // handle window resize
    window.addEventListener('resize', () => {
        location.reload();
    });
};