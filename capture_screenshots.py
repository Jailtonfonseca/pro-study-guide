from playwright.sync_api import sync_playwright, expect
import time

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})

        try:
            # Acessar a aplicação
            page.goto("http://localhost:8080")
            expect(page.locator("#dashboard-view")).to_be_visible()

            # Screenshot 1: Dashboard (Tela Inicial)
            # Criar um guia de exemplo para a screenshot não ficar vazia
            page.on("dialog", lambda dialog: dialog.accept("Introdução ao Docker"))
            page.get_by_role("button", name="Criar Novo Guia").click()

            # Aumentar muito o timeout aqui para esperar a geração dos tópicos pela API
            expect(page.locator("#editor-view")).to_be_visible(timeout=60000)

            page.get_by_role("button", name="← Voltar").click()
            expect(page.locator("#guide-list .guide-list-item")).to_be_visible()
            time.sleep(1) # Pequena pausa para garantir a renderização
            page.screenshot(path="docs/images/screenshot-dashboard.png")

            # Screenshot 2: Tela de Configurações
            page.get_by_role("link", name="Configurações").click()
            expect(page.locator("#settings-view")).to_be_visible()
            time.sleep(1)
            page.screenshot(path="docs/images/screenshot-settings.png")

            # Voltar para o dashboard e abrir o guia
            page.get_by_role("link", name="Meus Guias").click()
            expect(page.locator("#dashboard-view")).to_be_visible()
            page.get_by_role("button", name="Abrir").click()
            expect(page.locator("#editor-view")).to_be_visible()

            # Screenshot 3: Editor (com um tópico selecionado)
            expect(page.locator(".topic-item").first).to_be_visible(timeout=15000)
            page.locator(".topic-item").first.click()
            time.sleep(1)
            page.screenshot(path="docs/images/screenshot-editor.png")

            print("Screenshots capturadas com sucesso!")

        except Exception as e:
            print(f"Ocorreu um erro durante a captura de tela: {e}")
            page.screenshot(path="docs/images/error-screenshot.png")

        finally:
            browser.close()

if __name__ == "__main__":
    capture_screenshots()
