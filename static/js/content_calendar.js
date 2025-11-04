class ContentCalendar {
    constructor() {
        this.calendar = null;
        this.topics = [];
        this.scheduledContent = [];
        this.selectedTopic = null;
        this.init();
    }

    async init() {
        await this.loadTopics();
        this.initializeCalendar();
        this.bindEvents();
        this.updateStatistics();
    }

    async loadTopics() {
        try {
            const response = await fetch('/api/topics');
            const data = await response.json();
            this.topics = data;
            this.renderTopics();
        } catch (error) {
            console.error('Failed to load topics:', error);
            this.topics = this.getSampleTopics();
            this.renderTopics();
        }
    }

    getSampleTopics() {
        return [
            { id: 1, topic: "The Future of AI in Content Creation", style: "educational", points: ["AI transformation", "Human collaboration", "Personalization"] },
            { id: 2, topic: "How Agentic AI Systems Boost Business Efficiency", style: "case_study", points: ["85% error reduction", "$2.5M savings", "Real-time optimization"] },
            { id: 3, topic: "My Journey Building an AI Health Coach", style: "story", points: ["Personal frustration", "AI solution", "Life transformation"] },
            { id: 4, topic: "Understanding Large Language Models for Business", style: "educational", points: ["LLM basics", "Applications", "Limitations"] },
            { id: 5, topic: "AI in Customer Service: Beyond Chatbots", style: "insight", points: ["Predictive analytics", "Personalization", "Automation"] },
            { id: 6, topic: "The Evolution of AI: From Expert Systems to Generative Models", style: "educational", points: ["Historical perspective", "Current state", "Future outlook"] }
        ];
    }

    renderTopics() {
        const container = document.getElementById('topicSelection');
        container.innerHTML = this.topics.map(topic => `
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="topic-card card" data-topic-id="${topic.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title">${topic.topic}</h6>
                            <span class="style-badge style-${topic.style}">${topic.style}</span>
                        </div>
                        <ul class="small text-muted mb-0">
                            ${topic.points.map(point => `<li>${point}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `).join('');

        // Add click handlers
        document.querySelectorAll('.topic-card').forEach(card => {
            card.addEventListener('click', () => this.selectTopic(card));
        });
    }

    selectTopic(card) {
        // Remove previous selection
        document.querySelectorAll('.topic-card').forEach(c => c.classList.remove('selected'));

        // Add selection to clicked card
        card.classList.add('selected');

        const topicId = parseInt(card.dataset.topicId);
        this.selectedTopic = this.topics.find(t => t.id === topicId);
    }

    initializeCalendar() {
        const calendarEl = document.getElementById('calendar');
        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: false, // We use custom controls
            editable: true,
            droppable: true,
            selectable: true,
            events: [],
            eventClick: (info) => this.showEventDetails(info),
            dateClick: (info) => this.showDateDetails(info),
            drop: (info) => this.handleDrop(info),
            eventDrop: (info) => this.handleEventDrop(info)
        });

        this.calendar.render();
        this.updateCalendarTitle();
    }

    bindEvents() {
        // Navigation controls
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.calendar.prev();
            this.updateCalendarTitle();
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.calendar.next();
            this.updateCalendarTitle();
        });

        document.getElementById('currentMonth').addEventListener('click', () => {
            this.calendar.today();
            this.updateCalendarTitle();
        });

        // View controls
        document.getElementById('monthView').addEventListener('click', () => {
            this.calendar.changeView('dayGridMonth');
        });

        document.getElementById('weekView').addEventListener('click', () => {
            this.calendar.changeView('timeGridWeek');
        });

        document.getElementById('dayView').addEventListener('click', () => {
            this.calendar.changeView('timeGridDay');
        });

        // Quick actions
        document.getElementById('generateCalendar').addEventListener('click', () => this.generate30DayCalendar());
        document.getElementById('addRandomPost').addEventListener('click', () => this.addRandomPost());
        document.getElementById('fillWeek').addEventListener('click', () => this.fillThisWeek());
        document.getElementById('balancePlatforms').addEventListener('click', () => this.balancePlatforms());
        document.getElementById('clearCalendar').addEventListener('click', () => this.clearCalendar());

        // Drop zone
        const dropZone = document.getElementById('dropZone');
        dropZone.addEventListener('click', () => this.promptForDate());

        // Make topics draggable
        this.makeTopicsDraggable();
    }

    makeTopicsDraggable() {
        document.querySelectorAll('.topic-card').forEach(card => {
            card.draggable = true;

            card.addEventListener('dragstart', (e) => {
                const topicId = e.currentTarget.dataset.topicId;
                e.dataTransfer.setData('text/plain', topicId);
                e.currentTarget.classList.add('dragging');
            });

            card.addEventListener('dragend', (e) => {
                e.currentTarget.classList.remove('dragging');
            });
        });
    }

    updateCalendarTitle() {
        const title = this.calendar.currentData.viewTitle;
        document.getElementById('calendarTitle').textContent = title;
    }

    generate30DayCalendar() {
        if (!this.topics.length) {
            this.showNotification('No topics available', 'warning');
            return;
        }

        this.clearCalendar();
        const today = new Date();

        for (let i = 0; i < 30; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);

            // Alternate platforms for variety
            const platforms = ['linkedin', 'twitter', 'instagram'];
            const platform = platforms[i % platforms.length];

            // Select topic cyclically
            const topic = this.topics[i % this.topics.length];

            const event = {
                title: `${topic.topic} (${platform})`,
                start: date,
                allDay: true,
                backgroundColor: this.getPlatformColor(platform),
                extendedProps: {
                    topic: topic.topic,
                    style: topic.style,
                    platform: platform,
                    topicId: topic.id
                }
            };

            this.calendar.addEvent(event);
            this.scheduledContent.push(event);
        }

        this.updateStatistics();
        this.showNotification('30-day calendar generated successfully!', 'success');
    }

    addRandomPost() {
        if (!this.topics.length) {
            this.showNotification('No topics available', 'warning');
            return;
        }

        const randomTopic = this.topics[Math.floor(Math.random() * this.topics.length)];
        const platforms = ['linkedin', 'twitter', 'instagram'];
        const randomPlatform = platforms[Math.floor(Math.random() * platforms.length)];

        // Get current date or a random date in the next 30 days
        const today = new Date();
        const randomDays = Math.floor(Math.random() * 30);
        const date = new Date(today);
        date.setDate(today.getDate() + randomDays);

        const event = {
            title: `${randomTopic.topic} (${randomPlatform})`,
            start: date,
            allDay: true,
            backgroundColor: this.getPlatformColor(randomPlatform),
            extendedProps: {
                topic: randomTopic.topic,
                style: randomTopic.style,
                platform: randomPlatform,
                topicId: randomTopic.id
            }
        };

        this.calendar.addEvent(event);
        this.scheduledContent.push(event);
        this.updateStatistics();
        this.showNotification('Random post added to calendar!', 'success');
    }

    fillThisWeek() {
        if (!this.topics.length) {
            this.showNotification('No topics available', 'warning');
            return;
        }

        const today = new Date();
        const currentDay = today.getDay();
        const startOfWeek = new Date(today);
        startOfWeek.setDate(today.getDate() - currentDay);

        for (let i = 0; i < 7; i++) {
            const date = new Date(startOfWeek);
            date.setDate(startOfWeek.getDate() + i);

            // Skip past dates
            if (date < today) continue;

            const topic = this.topics[i % this.topics.length];
            const platforms = ['linkedin', 'twitter', 'instagram'];
            const platform = platforms[i % platforms.length];

            const event = {
                title: `${topic.topic} (${platform})`,
                start: date,
                allDay: true,
                backgroundColor: this.getPlatformColor(platform),
                extendedProps: {
                    topic: topic.topic,
                    style: topic.style,
                    platform: platform,
                    topicId: topic.id
                }
            };

            this.calendar.addEvent(event);
            this.scheduledContent.push(event);
        }

        this.updateStatistics();
        this.showNotification('This week filled with content!', 'success');
    }

    balancePlatforms() {
        const platforms = ['linkedin', 'twitter', 'instagram'];
        const currentEvents = this.calendar.getEvents();
        const platformCounts = {};

        platforms.forEach(platform => platformCounts[platform] = 0);

        currentEvents.forEach(event => {
            const platform = event.extendedProps.platform;
            if (platform) platformCounts[platform]++;
        });

        const maxCount = Math.max(...Object.values(platformCounts));
        const minCount = Math.min(...Object.values(platformCounts));

        if (maxCount - minCount <= 1) {
            this.showNotification('Platforms are already balanced!', 'info');
            return;
        }

        // Add content to underrepresented platforms
        const underrepresentedPlatforms = platforms.filter(p => platformCounts[p] < maxCount);

        underrepresentedPlatforms.forEach(platform => {
            const randomTopic = this.topics[Math.floor(Math.random() * this.topics.length)];
            const today = new Date();
            const randomDays = Math.floor(Math.random() * 30);
            const date = new Date(today);
            date.setDate(today.getDate() + randomDays);

            const event = {
                title: `${randomTopic.topic} (${platform})`,
                start: date,
                allDay: true,
                backgroundColor: this.getPlatformColor(platform),
                extendedProps: {
                    topic: randomTopic.topic,
                    style: randomTopic.style,
                    platform: platform,
                    topicId: randomTopic.id
                }
            };

            this.calendar.addEvent(event);
            this.scheduledContent.push(event);
        });

        this.updateStatistics();
        this.showNotification('Platforms balanced successfully!', 'success');
    }

    clearCalendar() {
        if (confirm('Are you sure you want to clear all scheduled content?')) {
            this.calendar.removeAllEvents();
            this.scheduledContent = [];
            this.updateStatistics();
            this.showNotification('Calendar cleared', 'info');
        }
    }

    handleDrop(info) {
        const topicId = parseInt(info.draggedEl.dataset.topicId);
        const topic = this.topics.find(t => t.id === topicId);

        if (!topic) return;

        const platforms = ['linkedin', 'twitter', 'instagram'];
        const platform = platforms[Math.floor(Math.random() * platforms.length)];

        const event = {
            title: `${topic.topic} (${platform})`,
            start: info.date,
            allDay: true,
            backgroundColor: this.getPlatformColor(platform),
            extendedProps: {
                topic: topic.topic,
                style: topic.style,
                platform: platform,
                topicId: topic.id
            }
        };

        this.calendar.addEvent(event);
        this.scheduledContent.push(event);
        this.updateStatistics();
        this.showNotification('Topic added to calendar!', 'success');
    }

    handleEventDrop(info) {
        this.showNotification('Content rescheduled!', 'info');
    }

    showEventDetails(info) {
        const event = info.event;
        const modal = new bootstrap.Modal(document.getElementById('contentModal'));

        document.getElementById('modalContent').innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h6>${event.extendedProps.topic}</h6>
                    <div class="mb-2">
                        <span class="style-badge style-${event.extendedProps.style}">${event.extendedProps.style}</span>
                        <span class="badge bg-secondary ms-2">${event.extendedProps.platform}</span>
                    </div>
                    <p class="text-muted">Scheduled for: ${event.start.toLocaleDateString()}</p>
                    <div class="content-preview">
                        <em>Content will be generated here. Click "Generate Content" to create the actual post.</em>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h6>Quick Actions</h6>
                            <div class="d-grid gap-2">
                                <button class="btn btn-sm btn-primary" onclick="calendar.generateContentForEvent('${event.id}')">
                                    <i class="bi bi-magic"></i> Generate
                                </button>
                                <button class="btn btn-sm btn-warning" onclick="calendar.rescheduleEvent('${event.id}')">
                                    <i class="bi bi-calendar"></i> Reschedule
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="calendar.removeEvent('${event.id}')">
                                    <i class="bi bi-trash"></i> Remove
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        modal.show();
    }

    showDateDetails(info) {
        if (this.selectedTopic) {
            const platforms = ['linkedin', 'twitter', 'instagram'];
            const platform = platforms[Math.floor(Math.random() * platforms.length)];

            const event = {
                title: `${this.selectedTopic.topic} (${platform})`,
                start: info.date,
                allDay: true,
                backgroundColor: this.getPlatformColor(platform),
                extendedProps: {
                    topic: this.selectedTopic.topic,
                    style: this.selectedTopic.style,
                    platform: platform,
                    topicId: this.selectedTopic.id
                }
            };

            this.calendar.addEvent(event);
            this.scheduledContent.push(event);
            this.updateStatistics();
            this.showNotification('Topic scheduled!', 'success');

            // Clear selection
            document.querySelectorAll('.topic-card').forEach(c => c.classList.remove('selected'));
            this.selectedTopic = null;
        } else {
            this.showNotification('Please select a topic first', 'warning');
        }
    }

    promptForDate() {
        const date = prompt('Enter date (YYYY-MM-DD):');
        if (date && this.selectedTopic) {
            const scheduledDate = new Date(date);
            if (!isNaN(scheduledDate.getTime())) {
                const platforms = ['linkedin', 'twitter', 'instagram'];
                const platform = platforms[Math.floor(Math.random() * platforms.length)];

                const event = {
                    title: `${this.selectedTopic.topic} (${platform})`,
                    start: scheduledDate,
                    allDay: true,
                    backgroundColor: this.getPlatformColor(platform),
                    extendedProps: {
                        topic: this.selectedTopic.topic,
                        style: this.selectedTopic.style,
                        platform: platform,
                        topicId: this.selectedTopic.id
                    }
                };

                this.calendar.addEvent(event);
                this.scheduledContent.push(event);
                this.updateStatistics();
                this.showNotification('Topic scheduled!', 'success');

                // Clear selection
                document.querySelectorAll('.topic-card').forEach(c => c.classList.remove('selected'));
                this.selectedTopic = null;
            } else {
                this.showNotification('Invalid date format', 'error');
            }
        } else if (!this.selectedTopic) {
            this.showNotification('Please select a topic first', 'warning');
        }
    }

    updateStatistics() {
        const events = this.calendar.getEvents();
        let linkedInCount = 0, twitterCount = 0, instagramCount = 0;

        events.forEach(event => {
            const platform = event.extendedProps.platform;
            if (platform === 'linkedin') linkedInCount++;
            else if (platform === 'twitter') twitterCount++;
            else if (platform === 'instagram') instagramCount++;
        });

        document.getElementById('totalPosts').textContent = events.length;
        document.getElementById('linkedInPosts').textContent = linkedInCount;
        document.getElementById('twitterPosts').textContent = twitterCount;
        document.getElementById('instagramPosts').textContent = instagramCount;
    }

    getPlatformColor(platform) {
        const colors = {
            linkedin: '#0077b5',
            twitter: '#1da1f2',
            instagram: '#e4405f'
        };
        return colors[platform] || '#667eea';
    }

    showNotification(message, type = 'info') {
        // Create toast notification
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.innerHTML = toastHtml;
        document.body.appendChild(toastContainer);

        const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
        toast.show();

        setTimeout(() => {
            document.body.removeChild(toastContainer);
        }, 5000);
    }
}

// Initialize calendar when page loads
let calendar;
document.addEventListener('DOMContentLoaded', () => {
    calendar = new ContentCalendar();
});