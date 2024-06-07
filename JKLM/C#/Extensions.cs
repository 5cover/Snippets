using System.Runtime.InteropServices;

namespace Scover.Jklm;

static class Extensions
{
    public static Dictionary<TSource, int> ToCounter<TSource>(
    this IEnumerable<TSource> source,
    IEqualityComparer<TSource>? comparer = default) where TSource : notnull
    {
        Dictionary<TSource, int> dictionary = new(comparer);
        foreach (TSource item in source) {
            CollectionsMarshal.GetValueRefOrAddDefault(dictionary, item, out _)++;
        }
        return dictionary;
    }
}