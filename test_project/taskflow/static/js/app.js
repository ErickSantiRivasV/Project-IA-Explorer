const form = document.querySelector("#task-form");
const titleInput = document.querySelector("#task-title");
const taskList = document.querySelector("#task-list");
const emptyState = document.querySelector("#empty-state");
const feedback = document.querySelector("#feedback");

async function request(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Ocurrió un error.");
    return data;
}

function renderTasks(tasks) {
    taskList.replaceChildren();
    emptyState.hidden = tasks.length > 0;

    for (const task of tasks) {
        const item = document.createElement("li");
        item.className = `task-item${task.completed ? " completed" : ""}`;

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = Boolean(task.completed);
        checkbox.setAttribute("aria-label", `Completar ${task.title}`);
        checkbox.addEventListener("change", async () => {
            try {
                await request(`/api/tasks/${task.id}`, { method: "PATCH" });
                await loadTasks();
            } catch (error) {
                feedback.textContent = error.message;
            }
        });

        const label = document.createElement("span");
        label.textContent = task.title;

        const removeButton = document.createElement("button");
        removeButton.className = "delete";
        removeButton.type = "button";
        removeButton.textContent = "Eliminar";
        removeButton.addEventListener("click", async () => {
            try {
                await request(`/api/tasks/${task.id}`, { method: "DELETE" });
                await loadTasks();
            } catch (error) {
                feedback.textContent = error.message;
            }
        });

        item.append(checkbox, label, removeButton);
        taskList.append(item);
    }
}

async function loadTasks() {
    const tasks = await request("/api/tasks");
    renderTasks(tasks);
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    feedback.textContent = "";
    try {
        await request("/api/tasks", {
            method: "POST",
            body: JSON.stringify({ title: titleInput.value })
        });
        titleInput.value = "";
        await loadTasks();
        titleInput.focus();
    } catch (error) {
        feedback.textContent = error.message;
    }
});

loadTasks().catch((error) => {
    feedback.textContent = error.message;
});
