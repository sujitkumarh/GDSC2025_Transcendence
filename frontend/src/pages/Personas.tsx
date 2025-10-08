export function Personas() {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Personas de Jovens Brasileiros</h1>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="font-semibold mb-2">Marina Silva</h3>
          <p className="text-sm text-gray-600 mb-2">19 anos • São Paulo, SP</p>
          <p className="text-sm mb-4">Interessada em energia solar e agricultura sustentável</p>
          <div className="badge-green">Interessada</div>
        </div>
      </div>
    </div>
  )
}