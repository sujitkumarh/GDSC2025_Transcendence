export function Admin() {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Painel Administrativo</h1>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Configurações do Sistema</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Modo do LLM</label>
              <select className="input-field">
                <option>Mock Mode (Desenvolvimento)</option>
                <option>AWS Mistral (Produção)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Idioma Padrão</label>
              <select className="input-field">
                <option>Português (pt-BR)</option>
                <option>English (en)</option>
              </select>
            </div>
          </div>
        </div>
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Status do Sistema</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>API Backend</span>
              <span className="badge-green">Ativo</span>
            </div>
            <div className="flex justify-between">
              <span>Agentes IA</span>
              <span className="badge-green">Operacional</span>
            </div>
            <div className="flex justify-between">
              <span>Telemetria</span>
              <span className="badge-green">Habilitada</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}