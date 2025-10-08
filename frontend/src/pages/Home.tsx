export function Home() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center py-16">
        <h1 className="text-5xl font-bold text-gradient mb-6">
          Transcendence
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Conectando jovens brasileiros com oportunidades de carreira verde através de assistência inteligente e orientação personalizada.
        </p>
        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="card text-center">
            <h3 className="text-xl font-semibold mb-4">🌱 Explore Carreiras Verdes</h3>
            <p className="text-gray-600">
              Descubra oportunidades em energia renovável, gestão de resíduos, agricultura sustentável e mais.
            </p>
          </div>
          <div className="card text-center">
            <h3 className="text-xl font-semibold mb-4">🤖 Assistente IA</h3>
            <p className="text-gray-600">
              Receba orientação personalizada baseada no seu perfil, localização e objetivos de carreira.
            </p>
          </div>
          <div className="card text-center">
            <h3 className="text-xl font-semibold mb-4">📚 Aprenda e Cresça</h3>
            <p className="text-gray-600">
              Acesse treinamentos, certificações e recursos educacionais para desenvolvimento profissional.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}