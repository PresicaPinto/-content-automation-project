class ContentDemo {
    constructor() {
        this.isGenerating = false;
        this.demoInterval = null;
        this.currentDemoIndex = 0;
        this.demoContent = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSampleContent();
        this.initializeMetrics();
    }

    bindEvents() {
        document.getElementById('startGeneration').addEventListener('click', () => this.startGeneration());
        document.getElementById('startAutoDemo').addEventListener('click', () => this.startAutoDemo());
        document.getElementById('pauseDemo').addEventListener('click', () => this.pauseDemo());
        document.getElementById('exportContent').addEventListener('click', () => this.exportContent());
    }

    async loadSampleContent() {
        try {
            const response = await fetch('/api/generator/latest');
            const data = await response.json();
            if (data.success && data.content) {
                this.demoContent = Array.isArray(data.content) ? data.content.slice(0, 3) : [data.content];
                this.populateCarousel();
            }
        } catch (error) {
            console.log('Using sample content for demo');
            this.demoContent = this.getSampleContent();
            this.populateCarousel();
        }
    }

    getSampleContent() {
        return [
            {
                topic: "The Future of AI in Content Creation",
                style: "educational",
                content: "## The Future of AI in Content Creation: Beyond Automation to Augmentation\n\nAI is rapidly reshaping content creation, moving far beyond simple automation. The future isn't about replacing human creativity, but about powerful augmentation. Here are three key insights driving this evolution:\n\n1. **Human-AI Collaboration Becomes the Standard:** The most impactful future lies in seamless collaboration. AI will handle heavy lifting like research, data analysis, initial drafting, and multilingual translation, freeing creators to focus on strategy, nuance, emotional intelligence, and high-level storytelling.\n\n2. **Hyper-Personalization at Scale:** AI will enable unprecedented levels of content tailored to individual preferences, behaviors, and contexts in real-time. Dynamic content generation, personalized video scripts, and adaptive learning paths will become commonplace, significantly boosting engagement and ROI.\n\n3. **Ethics and Authenticity Take Center Stage:** As AI-generated content proliferates, establishing clear ethical guidelines, ensuring transparency, and maintaining authenticity will be paramount for building trust and navigating intellectual property concerns responsibly."
            },
            {
                topic: "How Agentic AI Systems Boost Business Efficiency",
                style: "case_study",
                content: "### Case Study: How Agentic AI Systems Boost Business Efficiency\n\n**Problem:** A global retail company faced significant inefficiencies in its supply chain operations. Manual order processing led to a 40% error rate, causing delays in shipments and a 25% increase in operational costs. Additionally, customer support was overwhelmed with 5,000+ daily inquiries, resulting in a 60-minute average response time and a 15% drop in customer satisfaction.\n\n**Solution:** The company deployed an **Agentic AI system** to automate and optimize workflows. The AI agents integrated with inventory, logistics, and CRM platforms to:\n- Process orders autonomously using predictive analytics\n- Resolve 80% of customer queries via real-time chatbots with NLP capabilities\n- Dynamically reroute shipments based on demand forecasts and real-time disruptions\n\n**Result:** Within 6 months, the Agentic AI system delivered transformative results:\n- **Order processing errors reduced by 85%**, cutting operational costs by $1.2M annually\n- **Customer support response time slashed to 2 minutes**, boosting satisfaction by 35%\n- **Supply chain efficiency improved by 50%**, with a 20% faster delivery time and a 30% reduction in inventory waste\n\nBy leveraging autonomous decision-making and real-time data integration, the company achieved **$2.5M in annual savings** and enhanced scalability."
            },
            {
                topic: "My Journey Building an AI Health Coach",
                style: "story",
                content: "### My Journey Building an AI Health Coach: From Idea to Impact\n\n**The Beginning:** It started with a personal frustration. Like many busy professionals, I struggled to maintain consistent health habits. I had access to fitness apps, nutrition guides, and wearable devices, but none of them felt truly personalized or proactive. They tracked what I did, but couldn't anticipate what I needed.\n\n**The Turning Point:** One evening, after another missed workout and a poor dinner choice, I realized: what if AI could be like a personal health coach that truly understood me? Not just tracking data, but understanding patterns, predicting needs, and providing the right motivation at exactly the right time.\n\n**The Build:** I spent six months building an AI health coach that would:\n- Learn my energy patterns and suggest optimal workout times\n- Understand my stress levels and recommend appropriate activities\n- Analyze my nutrition habits and provide meal suggestions\n- Adjust recommendations based on real-time data from wearables\n- Send personalized motivation based on my personality and goals\n\n**The Breakthrough:** The moment everything clicked was when the system noticed I was consistently skipping afternoon workouts. Instead of just reminding me, it analyzed my calendar and stress levels, then suggested a different approach: shorter, more frequent movement breaks. It worked.\n\n**The Impact:** Today, I'm more consistent with my health habits than ever before. But the real breakthrough came when friends started asking to use it. That's when I realized this wasn't just a personal project anymore—it was a solution that could help millions of people take control of their health with personalized, AI-driven guidance."
            }
        ];
    }

    populateCarousel() {
        const carouselItems = document.querySelectorAll('#demoCarousel .carousel-item .content-preview');
        this.demoContent.forEach((content, index) => {
            if (carouselItems[index]) {
                carouselItems[index].innerHTML = `
                    <strong>${content.topic}</strong><br>
                    ${content.content.substring(0, 300)}...
                `;
            }
        });
    }

    async startGeneration() {
        if (this.isGenerating) return;

        this.isGenerating = true;
        const method = document.getElementById('generationMethod').value;
        const postCount = parseInt(document.getElementById('postCount').value);
        const style = document.getElementById('contentStyle').value;
        const platform = document.getElementById('platform').value;

        this.updateGenerationStatus('running', 'Starting content generation...');
        document.getElementById('generationResults').style.display = 'none';

        const startTime = Date.now();
        const estimatedTime = method === 'fast' ? postCount * 10 : postCount * 30;

        // Start progress animation
        this.animateProgress(estimatedTime);

        try {
            const response = await fetch('/api/generate/content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    num_posts: postCount,
                    platform: platform,
                    style: style,
                    use_fast: method === 'fast'
                })
            });

            const result = await response.json();

            if (result.success) {
                // Simulate generation time for demo purposes
                await this.simulateGeneration(postCount, method);

                const endTime = Date.now();
                const totalTime = (endTime - startTime) / 1000;
                const timePerPost = totalTime / postCount;

                this.displayResults(result, timePerPost, postCount);
                this.updateMetrics(timePerPost, postCount);
                this.updateGenerationStatus('complete', 'Generation completed successfully!');
            } else {
                this.updateGenerationStatus('error', `Generation failed: ${result.message}`);
            }
        } catch (error) {
            this.updateGenerationStatus('error', `Error: ${error.message}`);
        } finally {
            this.isGenerating = false;
            setTimeout(() => {
                this.updateGenerationStatus('ready', 'Ready to generate');
            }, 3000);
        }
    }

    async simulateGeneration(postCount, method) {
        const baseTime = method === 'fast' ? 2 : 5; // seconds per post
        const totalTime = baseTime * postCount;

        for (let i = 0; i < postCount; i++) {
            await new Promise(resolve => setTimeout(resolve, baseTime * 1000));
            this.updateGenerationStatus('running', `Generating post ${i + 1}/${postCount}...`);
        }
    }

    animateProgress(totalTime) {
        const duration = totalTime * 1000; // Convert to milliseconds
        const interval = 100; // Update every 100ms
        const steps = duration / interval;
        let currentStep = 0;

        const progressInterval = setInterval(() => {
            currentStep++;
            const progress = (currentStep / steps) * 100;

            this.updateGenerationStatus('running', `Generating... ${Math.round(progress)}%`);

            if (currentStep >= steps) {
                clearInterval(progressInterval);
            }
        }, interval);
    }

    updateGenerationStatus(status, message) {
        const statusElement = document.getElementById('generationStatus');
        const spinner = statusElement.querySelector('.loading-spinner');

        statusElement.className = 'generation-status';

        switch(status) {
            case 'ready':
                statusElement.classList.add('generation-ready');
                spinner.classList.remove('active');
                break;
            case 'running':
                statusElement.classList.add('generation-running');
                spinner.classList.add('active');
                break;
            case 'complete':
                statusElement.classList.add('generation-complete');
                spinner.classList.remove('active');
                break;
            case 'error':
                statusElement.classList.add('generation-error');
                spinner.classList.remove('active');
                break;
        }

        statusElement.querySelector('h6').textContent = message;
    }

    displayResults(result, timePerPost, postCount) {
        const resultsDiv = document.getElementById('generationResults');
        const contentOutput = document.getElementById('contentOutput');

        // Create sample results for demo
        const sampleResults = this.generateSampleResults(postCount);

        contentOutput.innerHTML = sampleResults.map((post, index) => `
            <div class="content-quality-card card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="card-title mb-0">Post ${index + 1}: ${post.topic}</h6>
                        <span class="style-badge style-${post.style}">${post.style}</span>
                    </div>
                    <div class="content-preview">
                        ${post.content.substring(0, 300)}...
                    </div>
                    <div class="row mt-3">
                        <div class="col-6">
                            <small class="text-muted"><i class="bi bi-clock"></i> ${timePerPost.toFixed(1)}s</small>
                        </div>
                        <div class="col-6 text-end">
                            <small class="text-success"><i class="bi bi-check-circle"></i> Quality: A+</small>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        resultsDiv.style.display = 'block';
    }

    generateSampleResults(count) {
        const styles = ['educational', 'case_study', 'story', 'insight'];
        const topics = [
            "The Future of AI in Content Creation",
            "How Agentic AI Systems Boost Business Efficiency",
            "My Journey Building an AI Health Coach",
            "Understanding Large Language Models for Business",
            "AI in Customer Service: Beyond Chatbots"
        ];

        return Array.from({length: count}, (_, i) => ({
            topic: topics[i % topics.length],
            style: styles[i % styles.length],
            content: this.demoContent[i % this.demoContent.length]?.content || "High-quality AI-generated content..."
        }));
    }

    updateMetrics(timePerPost, postCount) {
        // Update generation speed
        document.getElementById('generationSpeed').textContent = `${timePerPost.toFixed(1)}s`;

        // Update cache hit rate (mock data)
        const cacheHitRate = 60 + Math.random() * 30;
        document.getElementById('cacheHitRate').textContent = `${cacheHitRate.toFixed(0)}%`;

        // Update content quality score
        document.getElementById('contentQuality').textContent = 'A+';

        // Update performance meters
        document.getElementById('apiSavings').style.width = `${cacheHitRate}%`;
        document.getElementById('contentLength').style.width = '85%';
        document.getElementById('successRate').style.width = '95%';

        // Update speed comparison meter
        const speedImprovement = ((45 - timePerPost) / 45) * 100;
        document.getElementById('speedMeter').style.width = `${Math.max(0, speedImprovement)}%`;
    }

    initializeMetrics() {
        // Set initial metrics
        document.getElementById('generationSpeed').textContent = '10s';
        document.getElementById('cacheHitRate').textContent = '75%';
        document.getElementById('contentQuality').textContent = 'A+';
        document.getElementById('apiSavings').style.width = '75%';
        document.getElementById('contentLength').style.width = '85%';
        document.getElementById('successRate').style.width = '95%';
        document.getElementById('speedMeter').style.width = '70%';
    }

    startAutoDemo() {
        if (this.demoInterval) return;

        const carousel = new bootstrap.Carousel(document.getElementById('demoCarousel'));
        carousel.cycle();

        // Generate new content periodically
        this.demoInterval = setInterval(() => {
            this.generateDemoContent();
        }, 5000);

        // Update status
        const button = document.getElementById('startAutoDemo');
        button.innerHTML = '<i class="bi bi-stop-circle"></i> Stop Demo';
        button.onclick = () => this.stopAutoDemo();
    }

    stopAutoDemo() {
        if (this.demoInterval) {
            clearInterval(this.demoInterval);
            this.demoInterval = null;
        }

        const button = document.getElementById('startAutoDemo');
        button.innerHTML = '<i class="bi bi-play-circle"></i> Start Auto Demo';
        button.onclick = () => this.startAutoDemo();
    }

    pauseDemo() {
        const carousel = bootstrap.Carousel.getInstance(document.getElementById('demoCarousel'));
        if (carousel) {
            carousel.pause();
        }
    }

    async generateDemoContent() {
        // Simulate content generation during demo
        const styles = ['educational', 'case_study', 'story', 'insight'];
        const style = styles[Math.floor(Math.random() * styles.length)];

        try {
            const response = await fetch('/api/generate/content', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    num_posts: 1,
                    platform: 'linkedin',
                    style: style,
                    use_fast: true
                })
            });

            if (response.ok) {
                // Update metrics with new data
                this.updateMetrics(8 + Math.random() * 4, 1);
            }
        } catch (error) {
            console.log('Demo content generation simulation');
        }
    }

    exportContent() {
        const content = {
            generated_at: new Date().toISOString(),
            demo_content: this.demoContent,
            metrics: {
                generation_speed: document.getElementById('generationSpeed').textContent,
                cache_efficiency: document.getElementById('cacheHitRate').textContent,
                quality_score: document.getElementById('contentQuality').textContent
            },
            roi_calculation: {
                monthly_cost: '€110',
                revenue_goal: '€100,000',
                roi_multiple: '900x',
                break_even: '3 days'
            }
        };

        const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `content-automation-demo-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize demo when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ContentDemo();
});