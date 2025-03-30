
from dbmapper.match_result import MatchResult
from dbmapper.score import Score


class Matcher:

    @staticmethod
    def match(srcs: list, dsts: list, score_func, threshold=0.7) -> MatchResult:
        """
        Empareja dos listas de objetos (srcs y dsts) utilizando una función de puntuación.
        Args:
            srcs: Lista de objetos origen.
            dsts: Lista de objetos destino.
            score_func: Función de puntuación que calcula la similitud entre dos objetos.
            threshold: Umbral de similitud para considerar un emparejamiento válido.
        Returns:
            MatchResult: Resultado del emparejamiento.
        """
        srcs = sorted([ s for s in srcs ])
        dsts = sorted([ d for d in dsts ])

        # Calcula scores de similitud entre todas las tablas origen y destino
        all_scores : list[Score] = []
        for src in srcs:
            # Calcula el score de similitud entre el src y todos los dsts
            scores = [ score_func(src, dst, threshold) for dst in dsts]
            # Elimina los scores que no superan el umbral
            scores = [ score for score in scores if score.ratio > threshold ]
            # Añade todos los scores a la lista de scores
            all_scores.extend(scores)

        # Ordena los scores por ratio de similitud
        all_scores.sort(key=lambda score: score.ratio, reverse=True)

        # Escoge los mejores scores y los considera matches
        matched = []
        while all_scores:
            # Extrae el primer src score (el mejor candidato)
            best_score = all_scores.pop(0)
            # Añade el score a los matches
            matched.append(best_score)
            # Elimina todos los scores con el mismo src o dst
            all_scores = [ score for score in all_scores if score.src != best_score.src and score.dst != best_score.dst ]

        # Marca los srcs y dsts que no han sido emparejados
        unmatched_srcs = set(srcs) - set([ score.src for score in matched ])
        unmatched_dsts = set(dsts) - set([ score.dst for score in matched ])

        # Devuelve el resultado
        return MatchResult.create(
            matched = matched,
            unmatched_srcs = unmatched_srcs,
            unmatched_dsts = unmatched_dsts
        )