<?php

// This is a very quick and dirty webscraper that parses the dom for moon phase data for a given zip code
// returns a json encoded string structured like: { "2021-03-19": { "phase_name": "Waxing crescent, "percent": 31.9 }}
class WebScraper {

    const BASE_URL = "https://www.almanac.com/astronomy/moon/calendar/zipcode/11217/";
    
    const SPECIAL_MOONS = [
        'First Quarter' => 50,
        'Last Quarter' => 50,
        'New Moon' => 0,
        'Full Moon' => 100,
    ];

    public function scrape(string $date) {
        $url = self::BASE_URL . $date;
        try {
            libxml_use_internal_errors(true);
            $curl = curl_init($url);
            curl_setopt($curl, CURLOPT_RETURNTRANSFER, TRUE);
            curl_setopt($curl, CURLOPT_USERAGENT,'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13');

            $page = curl_exec($curl);
            curl_close($curl);
            $doc = new DomDocument();
            $doc->loadHTML($page);
            $els = $doc->getElementsByTagName('td');

            $day_to_percent_map = [];

            $data_map = [];
            foreach ($els as $el) {
                $date_number = null;
                $phase_name = null;
                $percent = null;
                $date_number = $el->getElementsByTagName('p')[0]->textContent;
                $date_number = str_pad($date_number, 2, '0', STR_PAD_LEFT);
                $phase_data = $el->getElementsByTagName('p')[1]->textContent;
                if ($phase_data === null) {
                    continue;
                }
                
                list($phase_name, $percent) = $this->getPhaseData($phase_data);
                if (in_array($phase_name, array_keys(self::SPECIAL_MOONS))) {
                    $percent = self::SPECIAL_MOONS[$phase_name];
                }

                $date_total = "$date-$date_number";
                $data_map[$date_total] = [
                    'phase_name' => $phase_name,
                    'percent' => (float) $percent,
                ];
            }

            return $data_map;
        } catch (Throwable $t) {
            var_dump($t->getMessage());
        }
    }

    private function getPhaseData(string $phase_data) {
        $phase_name_regex = '/\D+/';
        preg_match($phase_name_regex, $phase_data, $matches);
        if (empty($matches)) {
            $phase_name = null;
        } else {
            $phase_name = trim($matches[0]);
        }

        $percent_regex = '/[0-9.]+/';
        preg_match($percent_regex, $phase_data, $matches);
        if (empty($matches)) {
            $phase_name = $percent = null;
        } else {
            $percent = trim($matches[0]);
        }

        return [$phase_name, $percent];
    }
}

$dates = [
    '2021-01',
    '2021-02',
    '2021-03',
    '2021-04',
    '2021-05',
    '2021-06',
    '2021-07',
    '2021-08',
    '2021-09',
    '2021-10',
    '2021-11',
    '2021-12',
    '2022-01',
    '2022-02',
    '2022-03',
    '2022-04',
    '2022-05',
    '2022-06',
    '2022-07',
    '2022-08',
    '2022-09',
    '2022-10',
    '2022-11',
    '2022-12',
    '2023-01',
    '2023-02',
    '2023-03',
    '2023-04',
    '2023-05',
    '2023-06',
    '2023-07',
    '2023-08',
    '2023-09',
    '2023-10',
    '2023-11',
    '2023-12',
    '2024-01',
    '2024-02',
    '2024-03',
    '2024-04',
    '2024-05',
    '2024-06',
    '2024-07',
    '2024-08',
    '2024-09',
    '2024-10',
    '2024-11',
    '2024-12',
    '2025-01',
    '2025-02',
    '2025-03',
    '2025-04',
    '2025-05',
    '2025-06',
    '2025-07',
    '2025-08',
    '2025-09',
    '2025-10',
    '2025-11',
    '2025-12',
    '2026-01',
    '2026-02',
    '2026-03',
    '2026-04',
    '2026-05',
    '2026-06',
    '2026-07',
    '2026-08',
    '2026-09',
    '2026-10',
    '2026-11',
    '2026-12',
    '2027-01',
    '2027-02',
    '2027-03',
    '2027-04',
    '2027-05',
    '2027-06',
    '2027-07',
    '2027-08',
    '2027-09',
    '2027-10',
    '2027-11',
    '2027-12',
];

$scraper = new WebScraper();
$data_map = [];
$total_data = [];
foreach ($dates as $date) {
    $total_data = array_merge($total_data, $scraper->scrape($date));
}

file_put_contents('all_date_data.txt', json_encode($total_data), FILE_APPEND);
