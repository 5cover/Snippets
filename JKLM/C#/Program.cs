namespace Scover.Jklm;

static class Program
{
    static void Main()
    {
        // Read the syllables file and count the number of distinct syllabes
        var syllables = File.ReadLines("data/syllables.txt").ToCounter();

        // Read the words
        var words = File.ReadLines("data/liste_mots_all.txt");

        // Order words by the number of distinct syllables, prioritizing common ones
        var scores = words.Select(w => (word: w, score: Easiness(w))).OrderByDescending(i => i.score);

        foreach (var (word, score) in scores) {
            Console.WriteLine($"{word} : {score}");
        }

        int Easiness(string word)
        {
            // find the distinct syllables contained in word
            var containedSyllables = syllables.Where(kvp => word.Contains(kvp.Key)).ToList();
            // ponderate by the count
            return containedSyllables.Count * containedSyllables.Sum(kvp => kvp.Value);
        }
    }
}