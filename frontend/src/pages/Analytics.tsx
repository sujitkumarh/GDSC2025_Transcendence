export function Analytics() {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Análises e Métricas</h1>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card text-center">
          <h3 className="text-2xl font-bold text-green-600">8</h3>
          <p className="text-gray-600">Personas Ativas</p>
        </div>
        <div className="card text-center">
          <h3 className="text-2xl font-bold text-blue-600">24</h3>
          <p className="text-gray-600">Interações Totais</p>
        </div>
        <div className="card text-center">
          <h3 className="text-2xl font-bold text-yellow-600">89%</h3>
          <p className="text-gray-600">Taxa de Sucesso</p>
        </div>
        <div className="card text-center">
          <h3 className="text-2xl font-bold text-purple-600">3.2</h3>
          <p className="text-gray-600">Interações/Persona</p>
        </div>
      </div>
    </div>
  )
}