import { useEffect, useState } from 'react';

export default function GraphQLTest() {
  const [questions, setQuestions] = useState(null);

  useEffect(() => {
    async function fetchQuestions() {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_SUPABASE_URL}/graphql/v1`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            apikey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
            Authorization: `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`,
          },
          body: JSON.stringify({
            query: `
              query ListQuestions {
                questions {
                  id
                  content
                  author
                  upvotes
                  created_at
                }
              }
            `,
          }),
        }
      );
      const { data, errors } = await res.json();
      if (errors) {
        console.error('GraphQL errors:', errors);
      } else {
        console.log('GraphQL data:', data.questions);
        setQuestions(data.questions);
      }
    }
    fetchQuestions();
  }, []);

  if (!questions) return <p>Loading questions…</p>;
  return (
    <div style={{ padding: 20 }}>
      <h1>Supabase GraphQL Test</h1>
      <ul>
        {questions.map((q) => (
          <li key={q.id}>
            [{q.id}] {q.content} — by {q.author} ({q.upvotes} upvotes)
          </li>
        ))}
      </ul>
    </div>
  );
}
