import logging

log = logging.getLogger(__name__)


def drop_nomg(df):
    return df[df.index != 'no_mg']

def group_fits_in_parish(group, parish):
    return ((group.gsize + parish.occ < parish.psize) and
            ((group.gsize_h <= 0) or (group.gsize + parish.occ_h < parish.psize_h)))

def set_group_to_parish(group, parish, pilgrims, parishes):
    pilgrims.at[group.name, 'attributed_parish'] = parish.name
    parishes.at[parish.name, 'occ'] += group.gsize
    parish.occ  += group.gsize
    # This is not a bug. If one person is handi, then all group will go to handicap place.
    if group.gsize_h > 0:
        parishes.at[parish.name, 'occ_h'] += group.gsize
        parish.occ_h  += group.gsize

def fill_parish_with_groups(groups, parish, pilgrims, parishes):
    attributed_groups = []
    for gid, group in groups.iterrows():
        if group_fits_in_parish(group, parish):
            attributed_groups.append(gid)
            set_group_to_parish(group, parish, pilgrims, parishes)

    # remove groups already attributed from list
    groups = groups.loc[[gid for gid in groups.index if gid not in attributed_groups]]
    return groups



def initialize_allocation(parishes_raw, pilgrims_raw, all_neighbours, distance_matrix, language_seeds,
                          language_region_parishes):
    parishes = parishes_raw.copy()
    pilgrims = pilgrims_raw.copy()
    distance_matrix.columns = distance_matrix.columns.astype(int)
    all_neighbours.columns = all_neighbours.columns.astype(int)
    parishes['occ'] = 0
    parishes['occ_h'] = 0

    languages = language_seeds.sort_values("gsize", ascending=False).index.values

    for language in languages:
        logging.info(f"Preallocation of {language}")

        groups_of_language = pilgrims[pilgrims.glanguage == language].copy()
        groups_of_language.gsize_h = groups_of_language.apply(lambda row: row.gsize if row.gsize_h > 0 else 0, axis=1)
        macro_groups = (groups_of_language
                        .groupby('macro_group')[['gsize', 'gsize_h']]
                        .sum()
                        .sort_values('gsize', ascending=False)
                        .pipe(drop_nomg)
                        )

        allowed_parishes = language_region_parishes[language_region_parishes.glanguage == language].index.values
        ordered_pars = parishes.loc[allowed_parishes].sort_values('psize', ascending=False).index.values

        logging.info(f"Preallocating macro-groups group-by-group")
        for mgid, mcg in macro_groups.iterrows():
            logging.debug(f" - Macro-group: {mgid}")
            groups = pilgrims[pilgrims.macro_group == mgid].sort_values(['gsize_h', 'gsize'], ascending=False)

            for pid in ordered_pars:
                parish = parishes.loc[pid].copy()

                # check if entire macro_group fits in the parish (checking handicap if needed)
                if group_fits_in_parish(mcg, parish):
                    groups = fill_parish_with_groups(groups, parish, pilgrims, parishes)
                    if len(groups) != 0:
                        raise ValueError("Something went wrong: Couldn't find a spot for group when I should.")
                    # All groups of macro_group have been allocated, we can move to next one
                    break

                # check is macro-group cannot fit even in empty parish, i.e. needs to be split
                elif parish.occ == 0:
                    # first fill current parish as much as possible
                    groups = fill_parish_with_groups(groups, parish, pilgrims, parishes)

                    # find allowed neighbours (allowed parished restriction could be relaxed if needed)
                    new_par_ids_ser = all_neighbours[pid]
                    new_par_ids = new_par_ids_ser[new_par_ids_ser.isin(allowed_parishes)].values

                    for pid_new in new_par_ids:
                        parish_new = parishes.loc[pid_new].copy()
                        groups = fill_parish_with_groups(groups, parish_new, pilgrims, parishes)
                        if len(groups)==0:
                            break

                    if len(groups) != 0:
                        raise ValueError("Something went wrong: Searched everywhere with split and could not fit.")
                    else:
                        break
            else:
                raise ValueError("Failed to find a way to fit groups in nice way. Consider more aggressive split.")


        logging.info(f"Preallocating groups without macro_group")
        groups = groups_of_language[groups_of_language.macro_group == "no_mg"]
        for pid in ordered_pars:
            parish = parishes.loc[pid].copy()
            groups = fill_parish_with_groups(groups, parish, pilgrims, parishes)
            if len(groups) == 0:
                break
        else:
            raise ValueError("Failed to fit all independent groups in allowed parishes.")

    # Sanity Check
    parishes_raw['occ'] = 0
    parishes_raw['occ_h'] = 0
    for gid,group in pilgrims.iterrows():
        parishes_raw.at[group.attributed_parish, 'occ'] += group.gsize
        # This is not a bug. If one person is handi, then all group will go to handicap place.
        if group.gsize_h > 0:
            parishes_raw.at[group.attributed_parish, 'occ_h'] += group.gsize
    assert (parishes_raw.occ == parishes.occ).all()
    assert (parishes_raw.occ_h == parishes.occ_h).all()
    assert (parishes_raw.occ <= parishes_raw.psize).all()
    assert (parishes_raw.occ_h <= parishes_raw.psize_h).all()


    initial_allocation = pilgrims
    return initial_allocation
