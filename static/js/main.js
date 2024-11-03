document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('health-form');
    
    if (!form) {
        console.error('Form not found');
        return;
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // 初始化四个容器的内容（添加summary）
        const containers = {
            supplement: document.getElementById('supplement-container'),
            tcm: document.getElementById('tcm-container'),
            diet: document.getElementById('diet-container'),
            summary: document.getElementById('summary-container')  // 添加综合建议容器
        };
        
        // 清空所有容器
        Object.values(containers).forEach(container => {
            if (container) {
                // 创建内容div
                const contentDiv = document.createElement('div');
                contentDiv.className = 'typing-content';
                container.innerHTML = '';
                container.appendChild(contentDiv);
            }
        });

        // 累积的文本（添加summary）
        const accumulatedText = {
            supplement: '',
            tcm: '',
            diet: '',
            summary: ''  // 添加综合建议文本累积
        };

        const submitButton = document.querySelector('.submit-button');
        submitButton.disabled = true;
        submitButton.textContent = '生成中...';

        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const eventSource = new EventSource(`/submit?data=${encodeURIComponent(JSON.stringify(data))}`);
            
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    
                    // 同时更新四个容器（包括summary）
                    Object.keys(data).forEach(type => {
                        if (containers[type] && data[type]) {
                            accumulatedText[type] += data[type];
                            const contentDiv = containers[type].querySelector('.typing-content');
                            if (contentDiv) {
                                smoothlyUpdateContent(contentDiv, accumulatedText[type]);
                            }
                        }
                    });

                } catch (error) {
                    console.error('Error parsing SSE data:', error);
                }
            };

            // 平滑更新内容的函数
            function smoothlyUpdateContent(container, text) {
                // 使用marked.js解析markdown
                const htmlContent = marked.parse(text);
                
                // 获取容器的父元素（result-content）
                const parentContainer = container.parentElement;
                
                // 更新内容
                container.innerHTML = htmlContent;
                
                // 始终滚动到底部
                requestAnimationFrame(() => {
                    parentContainer.scrollTop = parentContainer.scrollHeight;
                });

                // 添加一个额外的检查，确保内容完全滚动到底部
                setTimeout(() => {
                    parentContainer.scrollTop = parentContainer.scrollHeight;
                }, 100);
            }

            eventSource.onerror = function(error) {
                console.error('SSE Error:', error);
                eventSource.close();
                submitButton.disabled = false;
                submitButton.textContent = '生成营养方案';
            };

            // 添加完成事件处理
            eventSource.addEventListener('complete', function(event) {
                eventSource.close();
                submitButton.disabled = false;
                submitButton.textContent = '生成营养方案';
            });

        } catch (error) {
            console.error('Error:', error);
            alert('提交失败，请重试');
            submitButton.disabled = false;
            submitButton.textContent = '生成营养方案';
        }
    });
});
