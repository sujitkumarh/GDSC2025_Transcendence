export function Assistant() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Assistente de Carreiras Verdes</h1>
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Chat com Assistente IA</h2>
            <div className="bg-gray-50 rounded-lg p-4 mb-4 h-96 overflow-y-auto">
              <p className="text-gray-600">Olá! Sou seu assistente para carreiras verdes. Como posso ajudar hoje?</p>
            </div>
            <div className="flex">
              <input 
                type="text" 
                placeholder="Digite sua pergunta sobre carreiras verdes..."
                className="input-field flex-1 mr-2"
              />
              <button className="btn-primary">Enviar</button>
            </div>
          </div>
        </div>
        <div className="space-y-4">
          <div className="card">
            <h3 className="font-semibold mb-2">Personas Disponíveis</h3>
            <select className="input-field">
              <option>Selecione uma persona...</option>
              <option>Marina Silva</option>
              <option>João Santos</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  )
}