from xml.dom.minidom import parseString

from client_order import ClientOrder

class XMLPARSER:

    @staticmethod
    def parse(data):

        # Parse the data into xml tree
        doc = parseString(data)

        # Get the name of the client
        name = doc.getElementsByTagName("Client")[0].getAttribute("NameId")
        print("Client Name: ", name)

        # Get the list of orders
        orders = doc.getElementsByTagName("Order")

        # For each order get the attributes
        for order in orders:
            
            number = order.getAttribute("Number")
            workpiece = order.getAttribute("WorkPiece")
            quantity = order.getAttribute("Quantity")
            date = order.getAttribute("DueDate")
            late = order.getAttribute("LatePen")
            early = order.getAttribute("EarlyPen")

            yield ClientOrder(name, str(number), workpiece, int(quantity), int(date), int(late), int(early))