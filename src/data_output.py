import xlsxwriter


class Output(object):
    def __init__(self, all_markets):
        self.all_markets = all_markets
        self.to_xls()

    def to_xls(self):
        print('to Xls')
        with xlsxwriter.Workbook('markets.xlsx') as workbook:
            worksheet = workbook.add_worksheet()
            for row, value in enumerate(self.all_markets):
                for col, data in enumerate(value):
                    worksheet.write(row, col, data)
